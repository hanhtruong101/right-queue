import { apiRequest, refreshCsrfToken, } from "../../../services/apiClient";
import type { CurrentUser, LoginCredentials } from "../types";

export function getCurrentUser(): Promise<CurrentUser> {
  return apiRequest<CurrentUser>("/auth/me/");
}

export async function login(
  credentials: LoginCredentials,
): Promise<CurrentUser> {
  await refreshCsrfToken();

  const user = await apiRequest<CurrentUser>("/auth/login/", {
    method: "POST",
    body: JSON.stringify(credentials),
  });

  // Django rotates its CSRF token during login.
  await refreshCsrfToken();

  return user;
}

export async function logout(): Promise<void> {
  await apiRequest<void>("/auth/logout/", {
    method: "POST",
  });
}