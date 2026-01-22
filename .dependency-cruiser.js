module.exports = {
  forbidden: [
    {
      name: "no-circular",
      severity: "error",
      from: {},
      to: {
        circular: true,
      },
    },
    {
      name: "no-deep-import",
      severity: "error",
      from: {},
      to: {
        path: ["(^|/)src/", "(^|/)internal/", "(^|/)__internal__/", "(^|/)dist/", "(^|/)lib/"],
      },
    },
  ],
  options: {
    doNotFollow: {
      path: "node_modules",
    },
    includeOnly: "^bin",
  },
};
