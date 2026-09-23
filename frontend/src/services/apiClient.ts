
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL?.replace(/\/+$/, "");

let csrfToken: string | null = null;

export class ApiError extends Error{
    status: number;
    data: unknown;

    constructor(status: number, data: unknown) {
    super("The API request failed.");
    this.status = status;
    this.data = data;
  }
}

export async function refreshCsrfToken(): Promise<string> {
    const response = await fetch(`${API_BASE_URL}/auth/csrf/`,{
        credentials: "include",
        headers:{
            Accept: "application/json",
        },
    });

    if(!response.ok){
        throw new ApiError(response.status, await response.text());
    }

    const data = (await response.json()) as {
        csrf_token: string;
    };

    csrfToken = data.csrf_token;
    return csrfToken;    
}

export async function apiRequest<T> (path: string, options: RequestInit={},):
    Promise<T>{
    const method = (options.method ?? "GET").toUpperCase();
    const unsafeMethods = ["POST", "PUT", "PATCH", "DELETE"];
    const headers = new Headers(options.headers);

    headers.set("Accept", "application/json");

    if(options.body){
        headers.set("Content-Type", "application/json");
    }

    if(unsafeMethods.includes(method)){
        const token = csrfToken ?? (await refreshCsrfToken());
        headers.set("X-CSRFToken", token);
    }

    const response = await fetch(`${API_BASE_URL}${path}`, {
        ...options,
        method,
        headers,
        credentials: "include",
    });

    if(response.status === 204){
        return undefined as T;
    }

    const data = await response.json().catch(()=>null);

    if(!response.ok){
        throw new ApiError(response.status, data);
    }
    return data as T;
}
