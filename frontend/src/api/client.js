const baseUrl = import.meta.env?.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api';

export class ApiClient {
  constructor(base = baseUrl, fetcher = fetch) {
    this.base = base.replace(/\/$/, '');
    this.fetcher = fetcher;
  }

  async request(path, options = {}) {
    let response;
    try {
      response = await this.fetcher(`${this.base}${path}`, {
        ...options,
        headers: { 'Content-Type': 'application/json', ...options.headers },
      });
    } catch {
      throw new Error('Cannot connect to the API. Check that the backend is running.');
    }
    const body = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(typeof body.detail === 'string' ? body.detail : `Request failed (${response.status}).`);
    }
    return body;
  }

  get(path) { return this.request(path); }
  post(path, body) { return this.request(path, { method: 'POST', body: JSON.stringify(body) }); }
}

export const api = new ApiClient();
