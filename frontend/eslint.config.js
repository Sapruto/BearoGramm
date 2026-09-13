import tseslint from 'typescript-eslint'

export default tseslint.config({
    files: ['**/*.ts', '**/*.tsx'],
    extends: [
        ...tseslint.configs.recommendedTypeChecked,
    ],
    languageOptions: {
        parserOptions: {
            projectService: true,
            tsconfigRootDir: import.meta.dirname,
        },
    },
    rules: {
        '@typescript-eslint/no-unnecessary-condition': 'error',
    },
})