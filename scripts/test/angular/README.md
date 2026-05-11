# Angular Judge0 Test Harness

This folder contains a minimal Angular component + Jest setup for Judge0 multi-file submissions.

## Install globally (once)

```powershell
npm install -g jest jest-environment-jsdom ts-jest typescript
```

## How to run locally

```powershell
$env:NODE_PATH = (npm root -g)
npm install
npx jest
```

## Files

- `package.json` — minimal Angular + Jest dependencies
- `tsconfig.json` — TypeScript compiler settings
- `jest.config.cjs` — ts-jest + jsdom test runner
- `src/app.component.ts` — Angular component
- `src/app.component.spec.ts` — Jest test for Angular component
