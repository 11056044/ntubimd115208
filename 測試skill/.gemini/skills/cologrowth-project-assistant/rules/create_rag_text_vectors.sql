create extension if not exists vector with schema extensions;

create table if not exists public.docs_vectors (
    id bigint generated always as identity not null,
    content text not null,
    metadata jsonb not null default '{}'::jsonb,
    embedding extensions.vector(1536) not null,
    constraint docs_vectors_pkey primary key (id)
) tablespace pg_default;

create index if not exists docs_vectors_embedding_idx on public.docs_vectors using ivfflat (embedding extensions.vector_cosine_ops)
with
    (lists = '100') tablespace pg_default;
