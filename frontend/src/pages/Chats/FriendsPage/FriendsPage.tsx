import type { FriendItemResponse } from '@/shared/api/friends';
import ProfileTrigger from '@/shared/components/ProfileCard/ProfileTrigger';
import { useChangeFriendStatus } from '@/shared/hooks/friends/useChangeFriendStatus';
import { useGetFriends } from '@/shared/hooks/friends/useGetFriends';
import { Check, Loader2, MessageCircle, UserPlus, X } from 'lucide-react';
import { useMemo, useState } from 'react';
import AddFriendForm from './AddFriendForm';

type Tab = 'all' | 'pending' | 'add';
type ViewStatus = 'friend' | 'incoming' | 'outgoing';

type FriendView = {
    id: string;
    status: ViewStatus;
    displayName: string;
    avatarUrl: string;
    bio: string;
};

const toView = (item: FriendItemResponse): FriendView[] => {
    let status: ViewStatus;

    if (item.status === 'accept') status = 'friend';
    else if (item.status === 'process') status = item.is_initiator ? 'outgoing' : 'incoming';
    else return [];

    return [
        {
            id: item.user_uuid,
            status,
            displayName: item.profile.name,
            avatarUrl: item.profile.avatar_url,
            bio: item.profile.bio,
        },
    ];
};

const FriendsPage = () => {
    const [tab, setTab] = useState<Tab>('all');

    const { data, isLoading, isError, fetchNextPage, hasNextPage, isFetchingNextPage } = useGetFriends(20);

    const friends = useMemo(() => data?.pages.flatMap((p) => p.items).flatMap(toView) ?? [], [data]);
    const { mutate: changeFriendStatus } = useChangeFriendStatus();

    const handleAccept = (id: string) => changeFriendStatus(
        { target_uuid: id, status: 'accept' },
    );
    const handleRemove = (id: string) => changeFriendStatus(
        { target_uuid: id, status: 'rejected' },
    );

    const receivedCount = friends.filter((f) => f.status === 'incoming').length;
    const hasPending = receivedCount + friends.filter((f) => f.status === 'outgoing').length > 0;

    const activeTab: Tab = tab === 'pending' && !hasPending ? 'all' : tab;

    const groups = (
        activeTab === 'all'
            ? [{ status: 'friend', title: 'Friends' }]
            : [
                { status: 'incoming', title: 'Received' },
                { status: 'outgoing', title: 'Sent' },
            ]
    )
        .map((g) => ({ ...g, items: friends.filter((f) => f.status === g.status) }))
        .filter((g) => g.items.length > 0);

    const tabClass = (id: Tab) =>
        `relative flex items-center gap-2 px-3 pb-3 text-sm transition-colors ${activeTab === id ? 'text-[#f4f4f5]' : 'text-[#8b8b93] hover:text-[#f4f4f5]'}`;

    const underline = <span className="absolute inset-x-0 -bottom-px h-0.5 rounded-full bg-[#f4f4f5]" />;

    return (
        <div className="h-full overflow-y-auto bg-[#0a0a0b] px-4 font-['Radio_Canada_Big',sans-serif] text-[#f4f4f5]">
            <div className="mx-auto w-full max-w-2xl">
                <div className="mt-5 flex items-center gap-1 border-b border-[#1a1a1d]">
                    <button onClick={() => setTab('all')} className={tabClass('all')}>
                        All
                        {activeTab === 'all' && underline}
                    </button>

                    {hasPending && (
                        <button onClick={() => setTab('pending')} className={tabClass('pending')}>
                            Pending
                            {receivedCount > 0 && (
                                <span className="flex h-4.5 min-w-4.5 items-center justify-center rounded-full bg-[#d22d39] px-1 text-[11px] font-medium leading-none text-white">
                                    {receivedCount}
                                </span>
                            )}
                            {activeTab === 'pending' && underline}
                        </button>
                    )}

                    <button
                        onClick={() => setTab('add')}
                        className={`mb-2 ml-1 flex h-8 items-center gap-1.5 rounded-lg px-3 text-[13px] font-medium transition-colors ${activeTab === 'add'
                            ? 'border border-[#4a4a52] bg-[#131316] text-[#f4f4f5]'
                            : 'bg-[#f4f4f5] text-[#0a0a0b] hover:opacity-90'
                            }`}
                    >
                        <UserPlus size={15} />
                        Add Friend
                    </button>
                </div>

                {activeTab === 'add' ? (
                    <div className="mt-6 rounded-xl border border-[#27272c] bg-[#0e0e10]/60 p-5">
                        <AddFriendForm />
                    </div>
                ) : isLoading ? (
                    <div className="mt-10 flex justify-center text-[#8b8b93]">
                        <Loader2 size={20} className="animate-spin" />
                    </div>
                ) : isError ? (
                    <p className="mt-10 text-center text-sm text-[#ef7878]">Failed to load friends</p>
                ) : groups.length === 0 ? (
                    <div className="mt-6 flex flex-col items-center gap-3 rounded-xl border border-dashed border-[#27272c] px-4 py-12 text-center">
                        <p className="text-sm text-[#5f5f66]">No friends yet — add your first one</p>
                        <button
                            onClick={() => setTab('add')}
                            className="h-9 rounded-lg bg-[#f4f4f5] px-4 text-[13px] font-medium text-[#0a0a0b] hover:opacity-90"
                        >
                            Add Friend
                        </button>
                    </div>
                ) : (
                    <div className="mt-6 flex flex-col gap-8 pb-8">
                        {groups.map(({ status, title, items }) => (
                            <section key={status}>
                                <h2 className="mb-2 px-1 text-xs font-medium uppercase tracking-wider text-[#8b8b93]">
                                    {title} — {items.length}
                                </h2>

                                <ul className="divide-y divide-[#1a1a1d] overflow-hidden rounded-xl border border-[#27272c]">
                                    {items.map((f) => (
                                        <li key={f.id} className="flex items-center gap-3 px-4 py-3 transition-colors hover:bg-[#0e0e10]">
                                            <ProfileTrigger userUUID={f.id}>
                                                <div className='flex flex-1 items-center gap-3 transition-colors hover:bg-[#0e0e10] cursor-pointer'>
                                                    <img
                                                        src={f.avatarUrl}
                                                        alt=""
                                                        className="h-10 w-10 shrink-0 rounded-full object-cover"
                                                    />

                                                    <div className="min-w-0 flex-1">
                                                        <p className="truncate text-sm">{f.displayName}</p>
                                                        {f.bio && <p className="truncate text-xs text-[#8b8b93]">{f.bio}</p>}
                                                    </div>
                                                </div>
                                            </ProfileTrigger>

                                            {f.status === 'incoming' && (
                                                <div className="flex gap-2">
                                                    <button
                                                        onClick={() => handleAccept(f.id)}
                                                        className="flex h-9 items-center gap-1.5 rounded-lg bg-[#f4f4f5] px-3 text-[13px] font-medium text-[#0a0a0b] hover:opacity-90"
                                                    >
                                                        <Check size={15} /> Accept
                                                    </button>
                                                    <button
                                                        onClick={() => handleRemove(f.id)}
                                                        aria-label="Decline"
                                                        className="flex h-9 w-9 items-center justify-center rounded-lg border border-[#27272c] text-[#8b8b93] hover:border-[#3a3a40] hover:text-[#ef7878]"
                                                    >
                                                        <X size={16} />
                                                    </button>
                                                </div>
                                            )}

                                            {f.status === 'outgoing' && (
                                                <button
                                                    onClick={() => handleRemove(f.id)}
                                                    className="h-9 rounded-lg border border-[#27272c] px-3 text-[13px] text-[#8b8b93] hover:border-[#3a3a40] hover:text-[#f4f4f5]"
                                                >

                                                    Cancel
                                                </button>
                                            )}

                                            {f.status === 'friend' && (
                                                <button
                                                    aria-label="Message"
                                                    className="flex h-9 w-9 items-center justify-center rounded-lg border border-[#27272c] text-[#8b8b93] hover:border-[#3a3a40] hover:text-[#f4f4f5]"
                                                >
                                                    <MessageCircle size={16} />
                                                </button>
                                            )}
                                        </li>
                                    ))}
                                </ul>
                            </section>
                        ))}

                        {hasNextPage && (
                            <button
                                onClick={() => fetchNextPage()}
                                disabled={isFetchingNextPage}
                                className="mx-auto flex h-9 items-center gap-2 rounded-lg border border-[#27272c] px-4 text-[13px] text-[#8b8b93] hover:border-[#3a3a40] hover:text-[#f4f4f5] disabled:opacity-60"
                            >
                                {isFetchingNextPage && <Loader2 size={14} className="animate-spin" />}
                                Load more
                            </button>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};

export default FriendsPage;