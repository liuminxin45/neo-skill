module.exports = {
  root: true,
  env: {
    es2021: true,
    node: true,
  },
  extends: ["eslint:recommended"],
  parserOptions: {
    ecmaVersion: 2021,
  },
  ignorePatterns: ["dist/", "build/", "reports/", "node_modules/", ".git/"],
  rules: {
    "max-lines-per-function": ["error", { max: 60, skipBlankLines: true, skipComments: true }],
    complexity: ["error", 15],
    "max-depth": ["error", 4],
    "no-eval": "error",
    "no-implied-eval": "error",
    "no-new-func": "error",
    "no-console": ["warn", { allow: ["warn", "error"] }],
    "no-var": "error",
    "prefer-const": "error",
    "no-unused-vars": ["error", { argsIgnorePattern: "^_", varsIgnorePattern: "^_" }],
    "no-path-concat": "error",
    "no-process-env": "off",
  },
};
