"""Core URL routes."""

from django.urls import path, include

from views import (
    qa,
    index,
    pregnancyrecordadd,
    userprofile,
    care_record,
    pregnancycase,
    login,
    edit_family_member,
    baby_home,
    baby_information,
    baby_record,
    baby_growthmap,
    ai_growth,
    social_sharing_card,
)


urlpatterns = [

    # ======================
    # 首頁
    # ======================
    path('', index.index, name='index'),


    # ======================
    # 登入 / 帳號
    # ======================
    path('login/', login.login_page, name='login'),

    path('accounts/', include('allauth.urls')),

    path(
        'google_auth_login/',
        login.google_auth_login,
        name='google_auth_login'
    ),

    path(
        'google_auth_login',
        login.google_auth_login,
        name='google_auth_login_no_slash'
    ),

    path(
        'api/auth/google/',
        login.google_auth_login
    ),

    path(
        'logout/',
        login.logout_user,
        name='logout'
    ),

    path(
        'demo_login/',
        login.demo_login,
        name='demo_login'
    ),


    # ======================
    # 育兒提醒
    # ======================
    path(
        'add_care_reminder/',
        care_record.add_care_reminder,
        name='add_care_reminder'
    ),

    path(
        'set_care_status/',
        care_record.set_care_status,
        name='set_care_status'
    ),


    # ======================
    # 孕期紀錄
    # ======================
    path(
        'pregnancyrecord/add/',
        pregnancyrecordadd.pregnancyrecord_add,
        name='pregnancy_record_add'
    ),

    path(
        'pregnancyrecord/',
        pregnancyrecordadd.pregnancyrecord,
        name='pregnancyrecord'
    ),

    path(
        'pregnancyrecord_new/',
        pregnancyrecordadd.pregnancyrecord_new,
        name='pregnancy_record_new'
    ),


    # ======================
    # 懷孕胎數
    # ======================
    path(
        'pregnancycase/',
        pregnancycase.pregnancy_case,
        name='pregnancy_case'
    ),

    path(
        'add_pregnancy_baby/',
        pregnancycase.add_pregnancy_case,
        name='add_pregnancy_case'
    ),

    path(
        'edit_pregnancy_case/',
        pregnancycase.edit_pregnancy_case,
        name='edit_pregnancy_case'
    ),


    # ======================
    # 嬰幼兒首頁
    # ======================
    path(
        'babyinformation/',
        baby_home.baby,
        name='babyinformation'
    ),


    # 嬰幼兒成長圖表
    path(
        'babygrowthmap/',
        baby_growthmap.baby_growthmap,
        name='babygrowthmap'
    ),


    # ======================
    # 嬰幼兒基本資料
    # ======================
    path(
        'add_baby_information/',
        baby_information.add_baby_information,
        name='add_baby_information'
    ),

    path(
        'edit_baby_information/',
        baby_information.edit_baby_information,
        name='edit_baby_information'
    ),

    path(
        'delete_baby_information/',
        baby_information.delete_baby_information,
        name='delete_baby_information'
    ),


    # ======================
    # 嬰幼兒成長紀錄
    # ======================
    path(
        'babyrecord/add/',
        baby_record.add_baby_record,
        name='add_baby_record'
    ),

    path(
        'babyrecord/edit/<int:babyrecord_id>/',
        baby_record.edit_baby_record,
        name='edit_baby_record'
    ),

    path(
        'babyrecord/<int:babyrecord_id>/delete/',
        baby_record.delete_baby_record,
        name='delete_baby_record'
    ),


    # ======================
    # AI 問答
    # ======================
    path(
        'qa/',
        qa.qa_conversation,
        name='qa_conversation'
    ),


    # ======================
    # AI 成長足跡
    # ======================
    path(
        'ai-growth/',
        ai_growth.ai_growth,
        name='ai_growth'
    ),


    # ======================
    # 社群分享卡片
    # ======================
    path(
        'social_sharing_card/',
        social_sharing_card.social_sharing_card_view,
        name='social_sharing_card'
    ),


    # ======================
    # 個人資料
    # ======================
    path(
        'userprofile/',
        userprofile.userprofile,
        name='profile'
    ),

    path(
        'edit_userprofile/',
        userprofile.edit_userprofile,
        name='edit_userprofile'
    ),

    path(
        'userprofile/update_profile/',
        userprofile.update_profile,
        name='update_profile'
    ),


    # ======================
    # 家庭照顧者
    # ======================
    path(
        'edit_family_member/',
        edit_family_member.edit_family_member,
        name='edit_family_member'
    ),

    path(
        'edit_helper_permissions/',
        edit_family_member.edit_helper_permissions,
        name='edit_helper_permissions'
    ),

    path(
        'join_family/',
        userprofile.join_family,
        name='join_family'
    ),


]
