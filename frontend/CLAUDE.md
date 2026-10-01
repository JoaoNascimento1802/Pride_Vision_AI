# Frontend — padrão e testes

> Regra-fonte: `AGENTS.md`. Aqui está o padrão local do React.

## Stack fixada pela especificação §8

React 19, Vite, TypeScript, Tailwind CSS 4, React Router, Axios, Recharts. Trocar
qualquer um destes exige AC novo em `SDD/09-arquitetura.md` — a spec nomeia a stack.

## Camadas

```
pages/       telas — uma por rota, dona do estado da tela
components/  pedaços reutilizáveis (Badges, Feedback, Layout)
hooks/       useRequisicao — os três estados (carregando, erro, dados)
api/         client.ts (única porta para o backend) + types.ts (contratos)
auth/        AuthContext + useAuth
```

**As telas nunca chamam `axios` diretamente.** Toda chamada passa por uma função
exportada de `api/client.ts`. É o que permite mockar a API no teste em um só lugar e o
que mantém o tratamento de 401 centralizado no interceptor.

**Toda busca de dado usa `useRequisicao`.** Ele já trata carregando, recarregando e erro.
Tela que faz `useEffect` + `useState` na mão esquece um dos três.

## Testes

Vitest + Testing Library, ambiente `jsdom`. Configuração em `vite.config.ts`, setup em
`src/setupTests.ts`.

```bash
cd frontend && npm run test
```

```bash
cd frontend && npm run test -- src/pages/__tests__/Dashboard.test.tsx
```

### Todo teste cita um AC

Igual ao backend: o ID entra no nome do caso, porque é ele que
`scripts/rastreabilidade.py` procura.

```tsx
it('AC-UI-01 — o dashboard mostra os cinco números da visão geral', async () => {
```

### O que mockar

Mocke as funções de `api/client.ts`, **não** o axios:

```tsx
vi.mock('../../api/client', () => ({
  obterDashboard: vi.fn(),
}))
```

Mockar o axios testaria o axios. Mockar `client.ts` testa a tela — que é o que o AC
descreve.

### O que asserir

O AC fala de comportamento observável, então o teste procura o que o usuário vê:
`getByText`, `getByRole`, `findByLabelText`. Nada de asserir estado interno de componente
nem contar renderizações.

Tela que depende de rota usa `MemoryRouter`; tela que depende de sessão usa o
`AuthContext` de verdade com um token falso no `localStorage`.

### Onde ficam

Co-locados em `__tests__/` ao lado do que testam:

```
src/pages/__tests__/Dashboard.test.tsx
src/components/__tests__/Badges.test.tsx
```

## Lint e build

```bash
cd frontend && npm run lint
```

```bash
cd frontend && npm run build
```

O `build` roda `tsc -b` antes do Vite: erro de tipo quebra o build de propósito.
