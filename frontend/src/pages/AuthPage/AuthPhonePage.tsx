import { parsePhoneNumberWithError } from 'libphonenumber-js';
import { useEffect, useRef, useState } from "react";
import { useNavigate } from 'react-router-dom';
import { useSendCode } from '../../shared/hooks/auth/useSendCode';
import { withPreventDefault } from '../../shared/lib/withPreventDefault';
import { useAuthStore } from '../../store/authStore';
import PhoneNumberInput, { type PhoneNumberInputRef } from "./PhoneNumberInput";

const AuthPhonePage = () => {
    const navigate = useNavigate();
    const [phone, setPhone] = useState('');
    const { phone: phoneStore, setPhone: setPhoneStore, setJustCreated } = useAuthStore();
    const { mutate: sendCode, isPending } = useSendCode();
    const phoneInputRef = useRef<PhoneNumberInputRef>(null);

    const handleSendCode = () => {
        if (!phoneInputRef.current?.validate())
            return;

        if (isPending)
            return;

        const rawPhone = parsePhoneNumberWithError(phone).number;

        sendCode(
            { phone_number: rawPhone },
            {
                onSuccess: (data) => {
                    setPhoneStore(rawPhone);
                    setJustCreated(!data.is_logining);
                    navigate("/auth/verify");
                }
            }
        )
    }

    useEffect(() => {
        if (phoneStore) {
            setPhone(phoneStore);
        }
    }, [])

    return (
        <div className="min-h-screen flex items-center justify-center bg-[#0a0a0b]">
            <form onSubmit={withPreventDefault(handleSendCode)} className="w-120 bg-[#131316] border border-[#1f1f23] rounded-2xl px-14 py-12">
                <div className="w-12 h-12 rounded-full bg-[#14243d] flex items-center justify-center mb-6">
                    <svg viewBox="0 0 24 24" fill="none" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-5.5 h-5.5 stroke-[#5b9bd8]">
                        <rect x="7" y="2" width="10" height="20" rx="2" />
                        <path d="M11 18h2" />
                    </svg>
                </div>

                <h1 className="text-[22px] font-medium text-[#f4f4f5] mb-1.5">
                    Enter your phone number
                </h1>
                <p className="text-sm text-[#8b8b93] mb-8 leading-relaxed">
                    We'll send you a code to verify it's you.
                </p>

                <PhoneNumberInput
                    ref={phoneInputRef}
                    value={phone}
                    onChange={setPhone}
                />

                <button
                    type='submit'
                    disabled={isPending}
                    className="w-full h-10.5 mt-6 rounded-[10px] bg-[#f4f4f5] text-[#0a0a0b] text-[15px] font-medium hover:bg-[#d4d4d8] transition-colors"
                >
                    {/* {isPending ? "Sending..." : "Send code"}*/} {/* Flickering on low latency */}
                    Send code
                </button>
            </form>
        </div>
    )
}

export default AuthPhonePage
