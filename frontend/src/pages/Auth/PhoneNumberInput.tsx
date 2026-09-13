import { isValidPhoneNumber } from 'libphonenumber-js';
import { AlertCircle } from 'lucide-react';
import { forwardRef, useImperativeHandle, useState } from 'react';
import { PhoneInput } from 'react-international-phone';
import 'react-international-phone/style.css';
import './phone-input-theme.css';

type Props = {
    value: string;
    onChange: (value: string) => void;
    error?: string | null;
    onValidate?: (isValid: boolean) => void;
    verifyOnBlur?: boolean;
};

export type PhoneNumberInputRef = {
    validate: () => boolean;
};

const PhoneNumberInput = forwardRef<PhoneNumberInputRef, Props>(
    ({ value, onChange, error, onValidate, verifyOnBlur = true }: Props, ref) => {
        const [localError, setLocalError] = useState<string | null>(null);

        const validate = (val: string, blur: boolean = false): boolean => {
            const setError = (msg: string) => {
                if (!verifyOnBlur && blur) return;
                setLocalError(msg);
                onValidate?.(false);
            };

            if (!val) {
                setError('Phone number is required');
                return false;
            }

            if (!isValidPhoneNumber(val)) {
                setError('Invalid phone number');
                return false;
            }

            setLocalError(null);
            onValidate?.(true);
            return true;
        };

        useImperativeHandle(ref, () => ({
            validate: () => validate(value),
        }));

        const displayError = error ?? localError;

        return (
            <div>
                <PhoneInput
                    defaultCountry="ru"
                    value={value}
                    onChange={onChange}
                    onBlur={() => validate(value, true)}
                    forceDialCode
                    preferredCountries={['ru', 'us']}
                    className={`w-full ${displayError ? 'phone-input--error' : ''}`}
                    inputClassName="w-full"
                />
                {displayError && (
                    <span style={{ display: 'flex', alignItems: 'center', gap: 4, marginTop: 4, fontSize: 13, color: '#ef7878' }}>
                        <AlertCircle size={14} style={{ flexShrink: 0 }} />
                        {displayError}
                    </span>
                )}
            </div>
        );
    }
);

export default PhoneNumberInput;