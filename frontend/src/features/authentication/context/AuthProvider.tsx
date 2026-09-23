import { useCallback, useEffect, useMemo, useState } from "react";
import type { PropsWithChildren } from "react";
import { getCurrentUser, login as loginRequest, logout as logoutRequest } from "../api/authApi";

import type { CurrentUser, LoginCredentials } from "../types";
import { AuthContext, type AuthContextValue } from "./AuthContext";

export const AuthProvider = ({children,}: PropsWithChildren)=>{
    const [user, setUser] = useState<CurrentUser | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    const refreshUser=useCallback(async()=>{
        try{
            const currentUser = await getCurrentUser();
            setUser(currentUser);
        }
        catch{
            setUser(null);
        }
        finally{
            setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        let isCurrent = true;

        const restoreSession = async () => {
            try {
                const currentUser = await getCurrentUser();
                if (isCurrent) {
                    setUser(currentUser);
                }
            } catch {
                if (isCurrent) {
                    setUser(null);
                }
            } finally {
                if (isCurrent) {
                    setIsLoading(false);
                }
            }
        };

        void restoreSession();

        return () => {
            isCurrent = false;
        };
    }, []);

    const login = useCallback(
        async(credentials: LoginCredentials) => {
            const currentUser = await loginRequest(credentials);
            setUser(currentUser);
        },[],
    );
    const logout = useCallback(async()=>{
        await logoutRequest();
        setUser(null);
    }, []);

    const value = useMemo<AuthContextValue>(()=>({
        user, isLoading, login, logout, refreshUser,
    }), [user, isLoading, login, logout, refreshUser],);
    return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}
