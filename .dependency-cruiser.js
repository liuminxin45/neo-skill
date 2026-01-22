module.exports = {
  forbidden: [
    {
      name: "no-circular",
      severity: "error",
      comment: "Circular dependencies make code harder to maintain and can cause runtime issues",
      from: {},
      to: {
        circular: true,
      },
    },
    {
      name: "no-deep-import",
      severity: "error",
      comment: "Only import from public entrypoints to maintain API boundaries",
      from: {},
      to: {
        path: ["(^|/)src/", "(^|/)internal/", "(^|/)__internal__/", "(^|/)dist/", "(^|/)lib/"],
      },
    },
    {
      name: "no-absolute-paths",
      severity: "error",
      comment: "Absolute paths harm portability across different environments",
      from: {},
      to: {
        path: ["^/home/", "^/Users/", "^C:\\\\", "^D:\\\\", "^E:\\\\"],
      },
    },
    {
      name: "no-orphans",
      severity: "warn",
      comment: "Orphan modules might indicate dead code",
      from: {
        orphan: true,
        pathNot: ["\\.(test|spec)\\.(js|ts)$", "^bin/"],
      },
      to: {},
    },
  ],
  options: {
    doNotFollow: {
      path: ["node_modules", "\\.git"],
    },
    includeOnly: "^bin",
    reporterOptions: {
      dot: {
        collapsePattern: "node_modules/[^/]+",
      },
    },
  },
};
