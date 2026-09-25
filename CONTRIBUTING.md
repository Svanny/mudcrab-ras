# Contributing

Issues and pull requests are welcome. Explain the problem, expected behavior and how to reproduce it. For geometry or process changes, cite the evidence and distinguish observations from reconstructed assumptions.

1. Fork the repository and create a branch.
2. Install Node 22.12+ and run `npm ci`.
3. Keep scene, controls, data and export concerns in their respective modules.
4. Run `npm test`, `npm run package:cad` and `npm run build`.
5. Check water, waste, electrical and air views, route isolation, play/pause, tour, keyboard operation and mobile layout. See `docs/verification.md`.
6. Open a pull request with the change and validation results. CI checks tests and the asset budget before deployment.

Change the native catalog and regenerate web data when modifying a connection. Preserve evidence gaps unless new source evidence resolves them. Do not add private reference documents, credentials, generated caches, `node_modules`, or large previews to the public repository.

By contributing, you agree that your contributions are licensed under the MIT License.
