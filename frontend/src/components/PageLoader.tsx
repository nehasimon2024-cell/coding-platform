const PageLoader = () => (
  <div className="flex h-screen items-center justify-center bg-admin-bg font-['Segoe_UI',sans-serif]">
    <div className="flex flex-col items-center gap-4">
      <div className="h-10 w-10 animate-spin rounded-full border-[3px] border-admin-orange/30 border-t-admin-orange"></div>
      <div className="text-sm font-semibold text-admin-text-muted">Loading app...</div>
    </div>
  </div>
);

export default PageLoader;
