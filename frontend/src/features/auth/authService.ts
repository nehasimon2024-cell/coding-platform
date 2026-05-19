import axiosInstance from "../../api/axiosInstance";
import useUserStore from "../../stores/userStore";
import { msalInstance, loginRequest } from "../../lib/msalConfig";
import type { User, UserRole } from "../../types/user";
import type { LoginResponse } from "./types/auth";

// ── Helpers ──────────────────────────────────────────────────────────────────

const isValidRole = (role: string): role is UserRole =>
  role === "admin" || role === "candidate";

function storeUser(response: LoginResponse): User {
  const { access_token, user: backendUser } = response;

  const user: User = {
    id: backendUser.user_id,
    name: backendUser.name,
    role: isValidRole(backendUser.role) ? backendUser.role : "candidate",
    department: backendUser.department ?? "N/A",
    token: access_token,
  };

  useUserStore.getState().setUser(user);
  return user;
}

// ── Auth functions ────────────────────────────────────────────────────────────

export const loginWithCredentials = async (
  email: string,
  password: string,
): Promise<User> => {
  const response = await axiosInstance.post<LoginResponse>("/auth/login", {
    email,
    password,
  });
  return storeUser(response.data);
};

export const loginWithSSO = async (): Promise<void> => {
  await msalInstance.initialize();
  await msalInstance.loginRedirect(loginRequest);
};

export const handleSSORedirectResult = async (): Promise<User | null> => {
  try {
    await msalInstance.initialize();
    const result = await msalInstance.handleRedirectPromise();
    if (!result || !result.idToken) return null;

    const response = await axiosInstance.post<LoginResponse>("/auth/sso", {
      id_token: result.idToken,
    });

    return storeUser(response.data);
  } catch (err) {
    console.error("[SSO] handleSSORedirectResult error:", err);
    return null;
  }
};

export const logout = async (): Promise<void> => {
  try {
    await axiosInstance.post("/auth/logout");
  } catch (err) {
    console.error("Logout failed", err);
  } finally {
    useUserStore.getState().clear();
    window.location.href = "/login";
  }
};

export const silentRefresh = async (): Promise<void> => {
  try {
    const response = await axiosInstance.post<LoginResponse>(
      "/auth/refresh",
      {},
      { withCredentials: true }
    );
    storeUser(response.data);
  } catch (err: any) {
    useUserStore.getState().clear();
  }
};
