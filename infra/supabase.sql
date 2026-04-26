-- Supabase pgvector setup for RAG Documentation Assistant

-- Enable the pgvector extension for vector operations
create extension if not exists vector;

-- Create the chunks table to store document embeddings
create table if not exists chunks (
  id          bigserial primary key,
  content     text not null,                    
  metadata    jsonb not null default '{}'::jsonb, 
  embedding   vector(384) not null             
);

-- Add a comment to clarify the table's purpose
comment on table chunks is 'Stores document chunks with embeddings for RAG retrieval';

-- Create an IVFFlat index for fast cosine similarity search
create index if not exists idx_chunks_embedding
  on chunks
  using ivfflat (embedding vector_cosine_ops)
  with (lists = 100);

-- Create a GIN index on data for fast JSONB filtering
create index if not exists idx_chunks_metadata
  on chunks
  using gin (metadata);

-- Create the RPC function for similarity search with collection filter
create or replace function match_chunks(
  query_embedding vector(384),   
  match_count     int,           
  p_collection    text         
)
returns table (
  id          bigint,
  content     text,
  metadata    jsonb,
  similarity  float
)
language sql stable
as $$
  select
    chunks.id,
    chunks.content,
    chunks.metadata,
    -- Cosine similarity = 1 - cosine distance
    1 - (chunks.embedding <=> query_embedding) as similarity
  from chunks
  where
    -- Filter chunks by the requested collection
    chunks.metadata->>'collection' = p_collection
  order by
    -- Sort by closest match
    chunks.embedding <=> query_embedding asc
  limit match_count;
$$;

-- Grant access so the Supabase API can call the RPC function
grant execute on function match_chunks(vector(384), int, text) to anon, authenticated, service_role;
