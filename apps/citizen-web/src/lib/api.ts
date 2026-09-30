export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8010";

async function check<T>(res: Response, what: string): Promise<T> {
  if (!res.ok) throw new Error(`${what} failed: ${res.status} ${await res.text()}`);
  return res.json() as Promise<T>;
}

export async function apiGet<T>(path: string): Promise<T> {
  return check<T>(await fetch(`${API_URL}${path}`, { cache: "no-store" }), `GET ${path}`);
}

export async function apiPost<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return check<T>(res, `POST ${path}`);
}

export async function apiPostForm<T>(path: string, form: FormData): Promise<T> {
  return check<T>(await fetch(`${API_URL}${path}`, { method: "POST", body: form }), `POST ${path}`);
}
