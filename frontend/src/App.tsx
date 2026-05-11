import { useEffect, useState } from "react";
import AppRoutes from "./routes/AppRoutes";
import PageLoader from "./components/PageLoader";
import { silentRefresh } from "./features/auth/authService";

const App = () => {
  const [isAuthenticating, setIsAuthenticating] = useState(true);

  useEffect(() => {
    silentRefresh().finally(() => setIsAuthenticating(false));
  }, []);

  if (isAuthenticating) {
    return <PageLoader />;
  }

  return <AppRoutes />;
};

export default App;
