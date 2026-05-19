import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import AppRoutes from "./routes/AppRoutes";
import PageLoader from "./components/PageLoader";
import { silentRefresh, handleSSORedirectResult } from "./features/auth/authService";

const App = () => {
  const [isAuthenticating, setIsAuthenticating] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    async function init() {
      const ssoUser = await handleSSORedirectResult();
      if (ssoUser) {
        const path =
          ssoUser.role === "admin" ? "/admin/dashboard" : "/candidate/dashboard";
        navigate(path, { replace: true });
        setIsAuthenticating(false);
        return;
      }

      await silentRefresh();
      setIsAuthenticating(false);
    }

    init();
  }, []);

  if (isAuthenticating) {
    return <PageLoader />;
  }

  return <AppRoutes />;
};

export default App;
