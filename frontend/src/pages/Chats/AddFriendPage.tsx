import { parsePhoneNumberWithError } from 'libphonenumber-js';
import { UserPlus } from 'lucide-react';
import { matchIsValidTel } from 'mui-tel-input';
import { useState } from 'react';
import toast from 'react-hot-toast';
import { useAddFriend } from '../../shared/hooks/personal/useAddFriend';
import { withPreventDefault } from '../../shared/lib/withPreventDefault';
import PhoneNumberInput from '../AuthPage/PhoneNumberInput';

const AddFriendPage = () => {
    const [phone, setPhone] = useState('');
    const [_phoneValid, setPhoneValid] = useState(false);

    const { mutate: sendAddFriend, isPending } = useAddFriend();

    const handleAddFriend = () => {
        if (!phone || !matchIsValidTel(phone)) return;

        const rawPhone = parsePhoneNumberWithError(phone).number;

        sendAddFriend(
            { other_user_phone: rawPhone },
            {
                onSuccess: () => {
                    toast.success('Friend added!');
                    setPhone('');
                },
            }
        );
    };

    return (
        <div className="flex-1 h-full flex items-center justify-center bg-[#0a0a0b]">
            <div className="w-120 bg-[#131316] border border-[#1f1f23] rounded-2xl px-14 py-12">
                <div className="w-12 h-12 rounded-full bg-[#14243d] flex items-center justify-center mb-6">
                    <UserPlus size={22} className="stroke-[#5b9bd8]" />
                </div>

                <h1 className="text-[22px] font-medium text-[#f4f4f5] mb-1.5">
                    Add a friend
                </h1>
                <p className="text-sm text-[#8b8b93] mb-8 leading-relaxed">
                    Enter their phone number to send a friend request.
                </p>

                <form onSubmit={withPreventDefault(handleAddFriend)}>
                    <PhoneNumberInput
                        value={phone}
                        onChange={setPhone}
                        onValidate={setPhoneValid}
                    />

                    <button
                        type="submit"
                        disabled={isPending}
                        className="w-full h-10.5 mt-6 rounded-[10px] bg-[#f4f4f5] text-[#0a0a0b] text-[15px] font-medium hover:bg-[#d4d4d8] transition-colors cursor-pointer"
                    >
                        Add friend
                    </button>
                </form>
            </div>
        </div>
    );
};

export default AddFriendPage;