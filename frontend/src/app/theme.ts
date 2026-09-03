import { createTheme } from '@mui/material/styles';


const theme = createTheme({
    palette: {
        mode: 'dark',
        background: {
            default: '#0a0a0b',
            paper: '#0e0e10',
        },
        text: {
            primary: '#f4f4f5',
            secondary: '#8b8b93',
        },
        divider: '#27272c',
        primary: {
            main: '#4a4a52',
            contrastText: '#0a0a0b',
        },
        error: {
            main: '#ef7878',
        },
    },
    components: {
        MuiOutlinedInput: {
            styleOverrides: {
                root: {
                    backgroundColor: '#0e0e10',
                    color: '#f4f4f5',
                    borderRadius: '10px',
                    '& .MuiOutlinedInput-notchedOutline': {
                        borderColor: '#27272c',
                    },
                    '&:hover .MuiOutlinedInput-notchedOutline': {
                        borderColor: '#3a3a40',
                    },
                    '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                        borderColor: '#4a4a52',
                        borderWidth: '1px',
                    },
                },
            },
        },
    },
});

export default theme;