export const withPreventDefault = <E extends React.SyntheticEvent>(
    handler: (e: E) => void
) => {
    return (e: E) => {
        e.preventDefault();
        handler(e);
    };
};