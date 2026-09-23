import { createContext } from "react";
import type { CurrentUser, LoginCredentials } from "../types";

export interface AuthContextValue{
    user: CurrentUser | null;
    isLoading: boolean;
    login: (credentials: LoginCredentials) => Promise<void>;
    logout: ()=> Promise<void>;
    refreshUser: ()=> Promise<void>;
}

export const AuthContext =
  createContext<AuthContextValue | undefined>(undefined);