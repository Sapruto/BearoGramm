import { Dialog } from '@mui/material';
import type { LucideIcon } from 'lucide-react';

type ConfirmDialogTone = 'danger' | 'neutral';

interface ConfirmDialogProps {
    open: boolean;
    title: string;
    description: string;
    icon: LucideIcon;
    confirmLabel: string;
    pendingLabel?: string;
    tone?: ConfirmDialogTone;
    isPending?: boolean;
    onConfirm: () => void;
    onClose: () => void;
}

const TONE_STYLES: Record<
    ConfirmDialogTone,
    { iconWrapper: string; icon: string; confirmButton: string }
> = {
    danger: {
        iconWrapper: 'bg-red-500/10 border-red-500/20',
        icon: 'text-red-400',
        confirmButton:
            'text-red-400 bg-red-500/10 border-red-500/20 hover:bg-red-500/20 hover:text-red-300 focus-visible:ring-red-500/50',
    },
    neutral: {
        iconWrapper: 'bg-[#1a1a1d] border-[#27272a]',
        icon: 'text-[#d4d4d8]',
        confirmButton:
            'text-[#f4f4f5] bg-[#27272a] border-[#3f3f46] hover:bg-[#3f3f46] focus-visible:ring-[#52525b]',
    },
};

export function ConfirmDialog({
    open,
    title,
    description,
    icon: Icon,
    confirmLabel,
    pendingLabel,
    tone = 'neutral',
    isPending = false,
    onConfirm,
    onClose,
}: ConfirmDialogProps) {
    const styles = TONE_STYLES[tone];

    return (
        <Dialog
            open={open}
            onClose={() => {
                if (!isPending) onClose();
            }}
            slotProps={{
                backdrop: {
                    sx: { backgroundColor: 'rgba(0, 0, 0, 0.65)', backdropFilter: 'blur(2px)' },
                },
                paper: {
                    sx: {
                        bgcolor: '#0f0f11',
                        backgroundImage: 'none',
                        color: '#f4f4f5',
                        borderRadius: '14px',
                        border: '1px solid #1f1f23',
                        boxShadow: '0 24px 60px rgba(0, 0, 0, 0.6)',
                        maxWidth: 440,
                        width: '100%',
                        m: 2,
                    },
                },
            }}
        >
            <div className="px-6 pt-6 pb-5 flex flex-col items-center text-center">
                <div
                    className={`w-11 h-11 rounded-full border flex items-center justify-center ${styles.iconWrapper}`}
                >
                    <Icon size={20} className={styles.icon} />
                </div>
                <h2 className="mt-4 text-base font-medium text-[#f4f4f5]">{title}</h2>
                <p className="mt-1.5 text-sm text-[#a1a1aa] text-balance">{description}</p>
            </div>

            <div className="px-6 pb-5 flex gap-2">
                <button
                    type="button"
                    autoFocus
                    disabled={isPending}
                    onClick={onClose}
                    className="flex-1 px-3.5 py-2 rounded-lg text-sm text-[#d4d4d8] bg-[#1a1a1d] hover:bg-[#27272a] hover:text-[#f4f4f5] transition-colors disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus-visible:ring-2 focus-visible:ring-[#3f3f46]"
                >
                    Cancel
                </button>
                <button
                    type="button"
                    disabled={isPending}
                    onClick={onConfirm}
                    className={`flex-1 px-3.5 py-2 rounded-lg text-sm font-medium border transition-colors disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus-visible:ring-2 ${styles.confirmButton}`}
                >
                    {isPending ? (pendingLabel ?? confirmLabel) : confirmLabel}
                </button>
            </div>
        </Dialog>
    );
}