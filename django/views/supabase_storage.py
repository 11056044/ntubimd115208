import logging
import mimetypes
import uuid
from urllib.parse import quote

import requests
from django.conf import settings

from views.upload_utils import InvalidImageError, validate_image_upload

TIMEOUT = 20
logger = logging.getLogger(__name__)


def _cfg():
    url = settings.SUPABASE_URL.rstrip('/')
    key = settings.SUPABASE_SERVICE_KEY
    bucket = getattr(settings, 'SUPABASE_BUCKET', 'photo')
    return url, key, bucket


def upload_image(uploaded, folder):
    """
    上傳圖片到 Supabase Storage。
    folder 例：f'baby_records/{baby_id}'、f'prenatal_records/{case_id}'
    回傳公開網址（存進資料表的 photo 欄位）；沒有檔案則回傳 None。

    驗證沿用專案既有的 validate_image_upload（副檔名由檔案內容決定，
    檔名一律用 uuid，不採用使用者輸入）。
    """
    if not uploaded:
        return None

    ext = validate_image_upload(uploaded)  # 不合法會丟 InvalidImageError
    uploaded.seek(0)
    if not ext.startswith('.'):
        ext = '.' + ext
    ctype = mimetypes.guess_type('x' + ext)[0] or 'application/octet-stream'

    url, key, bucket = _cfg()
    object_path = f'{folder.strip("/")}/{uuid.uuid4().hex}{ext}'
    endpoint = f'{url}/storage/v1/object/{bucket}/{quote(object_path)}'

    try:
        resp = requests.post(
            endpoint,
            headers={
                'Authorization': f'Bearer {key}',
                'apikey': key,
                'Content-Type': ctype,
                'x-upsert': 'false',
            },
            data=uploaded.read(),
            timeout=TIMEOUT,
        )
    except requests.RequestException as exc:
        # 連線層錯誤（網址錯、沒網路、逾時…）：詳細原因印在執行 runserver 的終端機
        logger.error('Supabase upload connection error: %r (endpoint=%s)', exc, endpoint)
        print(f'[Supabase 上傳失敗-連線] {exc!r}\n  endpoint={endpoint}')
        raise InvalidImageError('圖片上傳失敗，請稍後再試')
    if resp.status_code not in (200, 201):
        # Supabase 有回應但拒絕：狀態碼與訊息會說明原因（bucket 不存在、金鑰錯誤等）
        logger.error('Supabase upload failed: %s %s', resp.status_code, resp.text)
        print(f'[Supabase 上傳失敗] status={resp.status_code} body={resp.text}\n  endpoint={endpoint}')
        raise InvalidImageError('圖片上傳失敗，請稍後再試')

    return f'{url}/storage/v1/object/public/{bucket}/{quote(object_path)}'


def delete_image(public_url):
    """依公開網址刪除舊圖（盡力而為，失敗不影響主流程）。只處理自己 bucket 的網址。"""
    if not public_url:
        return
    try:
        url, key, bucket = _cfg()
        prefix = f'{url}/storage/v1/object/public/{bucket}/'
        if not public_url.startswith(prefix):
            return  # 舊的本機路徑或外部網址，不處理
        object_path = public_url[len(prefix):]
        requests.delete(
            f'{url}/storage/v1/object/{bucket}/{object_path}',
            headers={'Authorization': f'Bearer {key}', 'apikey': key},
            timeout=TIMEOUT,
        )
    except Exception:
        pass