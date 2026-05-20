import os
from supabase import create_client, Client

def get_client() -> Client:
    return create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])

def save_guide(content: str, filename: str):
    db = get_client()
    db.table("artem_guide").delete().neq("id", 0).execute()  # один гайд — один документ
    db.table("artem_guide").insert({"content": content, "filename": filename}).execute()

def get_guide() -> str:
    db = get_client()
    res = db.table("artem_guide").select("content").limit(1).execute()
    if res.data:
        return res.data[0]["content"]
    return ""

def save_posts(posts: list[str], source_file: str):
    db = get_client()
    rows = [{"content": p, "source_file": source_file} for p in posts]
    db.table("artem_posts").insert(rows).execute()

def get_posts(limit: int = 30) -> list[str]:
    db = get_client()
    res = db.table("artem_posts").select("content").limit(limit).execute()
    return [r["content"] for r in res.data]

def clear_posts():
    db = get_client()
    db.table("artem_posts").delete().neq("id", 0).execute()
