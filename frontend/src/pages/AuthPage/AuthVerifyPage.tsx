import { parsePhoneNumberWithError } from 'libphonenumber-js';
import { ArrowLeft, ShieldCheck } from "lucide-react";
import { MuiOtpInput } from 'mui-one-time-password-input';
import { useEffect, useState } from "react";
import toast from 'react-hot-toast';
import { useNavigate } from "react-router-dom";
import { useVerifyCode } from '../../shared/hooks/auth/useVerifyCode';
import { useAuthStore } from "../../store/authStore";
const AuthVerifyPage = () => {
    const navigate = useNavigate();
    const { phone, setToken } = useAuthStore();
    const [phoneFormatted, setPhoneFormatted] = useState('');
    const [otp, setOtp] = useState('')

    const { mutate: verifyCode, isPending, error } = useVerifyCode();

    useEffect(() => {
        if (!phone) {
            navigate("/auth/phone", { replace: true })
        }
    }, [])

    useEffect(() => {
        if (!phone)
            return;

        const formatted = parsePhoneNumberWithError(phone).format("INTERNATIONAL")
        setPhoneFormatted(formatted);
    }, [phone])

    const handleChange = (newValue: string) => {
        setOtp(newValue)
    }

    const handleVerify = () => {
        if (otp.length !== 5)
            return;

        verifyCode(
            { phone_number: phone, code: otp },
            {
                onSuccess: (data) => {
                    setToken(data.token);
                    navigate("/", { replace: true })
                    toast.success("Successfully signed in!")
                }
            }
        )
    }


    return (
        <div className="min-h-screen flex items-center justify-center bg-[#0a0a0b]">
            <div className="w-120 bg-[#131316] border border-[#1f1f23] rounded-2xl px-14 py-12">
                <div className="w-12 h-12 rounded-full bg-[#132414] flex items-center justify-center mb-6">
                    <ShieldCheck size={22} className="stroke-[#6fbf6f]" />
                </div>

                <h1 className="text-[22px] font-medium text-[#f4f4f5] mb-1.5">Enter the code</h1>
                <p className="text-sm text-[#8b8b93] mb-8 leading-relaxed">
                    We sent a 5-digit code to <span className="text-[#f4f4f5] font-medium">{phoneFormatted}</span>
                </p>

                <MuiOtpInput
                    length={5}
                    value={otp}
                    onChange={handleChange}
                    TextFieldsProps={{
                        placeholder: '',
                        sx: {
                            '& .MuiOutlinedInput-root': {
                                height: 56,
                                fontSize: '20px',
                            },
                        },
                    }}
                    className="mb-6"
                />

                {/* <p className="text-sm text-[#8b8b93] mb-8">
                    Didn't get a code? <span className="text-[#5b9bd8] cursor-pointer">Resend in 0:42</span>
                </p> */}

                <button
                    onClick={handleVerify}
                    disabled={isPending}
                    className="w-full h-10.5 mb-2 rounded-[10px] bg-[#f4f4f5] text-[#0a0a0b] text-[15px] font-medium hover:bg-[#d4d4d8] transition-colors"
                >
                    {/* {isPending ? 'Verifying...' : 'Verify'} */}
                    Verify
                </button>
                <button
                    className="w-full h-10.5 rounded-[10px] border border-[#27272c] text-[#f4f4f5] text-[15px] font-medium flex items-center justify-center gap-1.5 hover:bg-[#1a1a1d] transition-colors"
                    onClick={() => navigate("/auth/phone")}
                >
                    <ArrowLeft size={15} />
                    Change number
                </button>
            </div>
        </div>
    )
}

export default AuthVerifyPage