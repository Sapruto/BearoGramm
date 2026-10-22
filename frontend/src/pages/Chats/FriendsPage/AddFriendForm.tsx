import PhoneNumberInput, { type PhoneNumberInputRef } from '@/pages/Auth/PhoneNumberInput';
import { useSendFriendRequest } from '@/shared/hooks/friends/useSendFriendRequest';
import { AlertCircle, AtSign, Check, Phone, UserPlus } from 'lucide-react';
import { useRef, useState } from 'react';

export type AddFriendMode = 'username' | 'phone';

type Props = {
    className?: string;
};

const modes = [
    { id: 'username' as const, label: 'Username', hint: 'Find someone by their @username', icon: AtSign },
    { id: 'phone' as const, label: 'Phone number', hint: 'Find someone by their phone number', icon: Phone },
];

const AddFriendForm = ({ className = '' }: Props) => {
    const [mode, setMode] = useState<AddFriendMode>('username');
    const [username, setUsername] = useState('');
    const [phone, setPhone] = useState('');
    const [usernameError, setUsernameError] = useState<string | null>(null);
    const [sentTo, setSentTo] = useState<string | null>(null);
    const phoneRef = useRef<PhoneNumberInputRef>(null);
    const { mutate: sendFriendRequest, isPending } = useSendFriendRequest();

    const current = modes.find((m) => m.id === mode)!;

    const selectMode = (id: AddFriendMode) => {
        setMode(id);
        setSentTo(null);
    };

    const addFriend = (value: string, value_type: 'phone' | 'username') => {
        sendFriendRequest(
            { target_type: value_type, target_value: value },
            {
                onSuccess: () => {
                    setSentTo(`@${value}`);

                    if (value_type == 'phone')
                        setPhone('');
                    else
                        setUsername('');

                    setTimeout(() => setSentTo(null), 3500);
                }
            }
        )
    }

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();


        if (mode === 'phone') {
            if (!phoneRef.current?.validate())
                return;
            addFriend(phone, 'phone');
        } else {
            const value = username.trim().replace(/^@/, '');
            if (!/^[a-zA-Z0-9_.]{3,32}$/.test(value)) {
                setUsernameError('Use 3–32 characters: letters, numbers, _ and .');
                return;
            }
            addFriend(value, 'username');
        }

        setUsernameError(null);
    };

    return (
        <form onSubmit={handleSubmit} className={className}>
            <div className="mb-3 flex gap-5 border-b border-[#1a1a1d]">
                {modes.map(({ id, label }) => (
                    <button
                        key={id}
                        type="button"
                        onClick={() => selectMode(id)}
                        className={`relative pb-2.5 text-sm transition-colors ${mode === id ? 'text-[#f4f4f5]' : 'text-[#8b8b93] hover:text-[#f4f4f5]'}`}
                    >
                        {label}
                        {mode === id && <span className="absolute inset-x-0 -bottom-px h-0.5 rounded-full bg-[#f4f4f5]" />}
                    </button>
                ))}
            </div>
            <p className="mb-3 text-[13px] text-[#8b8b93]">{current.hint}</p>

            <div className="flex flex-col items-stretch gap-2 sm:flex-row sm:items-start">
                <div className="min-w-0 flex-1">
                    {mode === 'phone' ? (
                        <PhoneNumberInput ref={phoneRef} value={phone} onChange={setPhone} verifyOnBlur={false} />
                    ) : (
                        <div>
                            <div className="relative">
                                <AtSign size={16} className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-[#5f5f66]" />
                                <input
                                    value={username}
                                    onChange={(e) => {
                                        setUsername(e.target.value);
                                        setUsernameError(null);
                                    }}
                                    placeholder="username"
                                    autoComplete="off"
                                    spellCheck={false}
                                    className={`h-14 w-full rounded-[10px] border bg-[#0e0e10] pl-10 pr-4 text-[0.9rem] text-[#f4f4f5] outline-none transition-colors placeholder:text-[#8b8b93] ${usernameError
                                        ? 'border-[#ef7878]'
                                        : 'border-[#27272c] hover:border-[#3a3a40] focus:border-[#4a4a52]'
                                        }`}
                                />
                            </div>
                            {usernameError && (
                                <span className="mt-1 flex items-center gap-1 text-[13px] text-[#ef7878]">
                                    <AlertCircle size={14} className="shrink-0" />
                                    {usernameError}
                                </span>
                            )}
                        </div>
                    )}
                </div>

                <button
                    type="submit"
                    disabled={isPending}
                    className="flex h-14 shrink-0 items-center justify-center gap-2 rounded-[10px] bg-[#f4f4f5] px-5 text-sm font-medium text-[#0a0a0b] transition-opacity hover:opacity-90 active:opacity-80"
                >
                    <UserPlus size={16} />
                    Send request
                </button>
            </div>

            {sentTo && (
                <p className="mt-3 flex items-center gap-1.5 text-[13px] text-[#8b8b93]">
                    <Check size={14} className="text-[#f4f4f5]" />
                    Request sent to <span className="text-[#f4f4f5]">{sentTo}</span>
                </p>
            )}
        </form>
    );
};

export default AddFriendForm;