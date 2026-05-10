import { create } from "zustand";

import type { User } from "../types/user";

type UserStore = User & {
  setUser: (user: User) => void;
  clear: () => void;
};

const initialState: User = {
  id: null,
  name: null,
  role: null,
  token: null,
  department: null,
};

const useUserStore = create<UserStore>()((set) => ({
  ...initialState,
  setUser: (user) => set(() => ({ ...user })),
  clear: () => set(() => ({ ...initialState })),
}));

export { useUserStore }
export default useUserStore