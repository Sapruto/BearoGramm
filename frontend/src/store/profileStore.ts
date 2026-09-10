import { create } from 'zustand';
import type { Profile } from '../shared/api/profile';

type ProfileStore = {
    profile: Profile | null;
    setProfile: (profile: Profile) => void;
};

export const useProfileStore = create<ProfileStore>()(
    (set) => ({
        profile: null,
        setProfile: (profile) => set({ profile })
    })
);