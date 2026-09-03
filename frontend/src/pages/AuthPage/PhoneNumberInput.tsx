import { validatePhoneNumberLength, type CountryCode } from 'libphonenumber-js';
import { AlertCircle } from 'lucide-react';
import { matchIsValidTel, MuiTelInput, type MuiTelInputInfo } from 'mui-tel-input';
import { useEffect, useRef, useState } from 'react';
function isPhoneNumberTooLong(phoneNumber: string, countryCode: CountryCode | null) {
    const lengthResult = validatePhoneNumberLength(phoneNumber, countryCode ?? undefined);
    return lengthResult === "INVALID_LENGTH" || lengthResult === "TOO_LONG";
}

function truncatePhoneNumber(phoneNumber: string, countryCode: CountryCode | null) {
    while (isPhoneNumberTooLong(phoneNumber, countryCode)) {
        phoneNumber = phoneNumber.slice(0, -1);
    }
    return phoneNumber;
}

type Props = {
    value: string;
    onChange: (value: string) => void;
    error?: string | null;
    onValidate?: (isValid: boolean) => void;
};

const PhoneNumberInput = ({ value, onChange, error, onValidate }: Props) => {
    const [inputKey, setInputKey] = useState(0);
    const inputRef = useRef<HTMLInputElement>(null);
    const [localError, setLocalError] = useState<string | null>(null);

    const validate = (val: string): boolean => {
        if (!val) {
            setLocalError("Phone number is required");
            onValidate?.(false);
            return false;
        }

        if (!matchIsValidTel(val)) {
            setLocalError('Invalid phone number');
            onValidate?.(false);
            return false;
        }

        setLocalError(null);
        onValidate?.(true);
        return true;
    };

    const handleChange = (newValue: string, info: MuiTelInputInfo) => {
        if (info.reason === "country") {
            onChange(truncatePhoneNumber(newValue, info.countryCode));
            return;
        }

        if (isPhoneNumberTooLong(newValue, info.countryCode)) {
            setInputKey(k => k + 1);
            return;
        }

        onChange(newValue);
    };

    useEffect(() => {
        if (inputKey > 0) {
            inputRef.current?.focus();
        }
    }, [inputKey]);

    const displayError = error ?? localError;

    return (
        <MuiTelInput
            className='w-full'
            key={inputKey}
            inputRef={inputRef}
            value={value}
            onChange={handleChange}
            onBlur={() => validate(value)}
            defaultCountry="RU"
            forceCallingCode
            preferredCountries={["RU", "US"]}
            error={!!displayError}
            helperText={
                displayError ? (
                    <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                        <AlertCircle size={14} style={{ flexShrink: 0 }} />
                        {displayError}
                    </span>
                ) : ''
            }
        />
    );
};

export default PhoneNumberInput;