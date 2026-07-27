# Zod + Formik, From Zero

Two separate problems live in every form: *is this data valid?* and *what is the user currently doing?* Zod answers the first, Formik the second, and this article builds each from its own starting point before wiring them together. Along the way you'll meet the idea that makes Zod matter far beyond forms: TypeScript types stop existing at runtime, and something has to stand guard where they can't.

---

## 1. The Problem Zod Solves: Your Types Are a Belief, Not a Fact

TypeScript feels like safety:

```typescript
interface Account {
  id: number;
  balance: number;
}

const account: Account = await fetch('/api/v1/accounts/7').then((r) => r.json());
console.log(account.balance.toFixed(2));
```

But `.json()` returns `any`, and the annotation `: Account` is a *promise you made to the compiler*, not a check. TypeScript types are **erased at compile time** — at runtime there is no `Account`, no `number`, nothing verifying that the API actually sent what you believe. If the backend renames `balance` to `currentBalance`, this code still compiles, still runs, and crashes later with `undefined is not a function` in a component three files away — the frontend twin of the untyped-dict problem Pydantic solves in Python ([04_pydantic.md](04_pydantic.md)).

Zod is a validator that lives at runtime. You declare the shape once, as a value:

```typescript
import { z } from 'zod';

const AccountSchema = z.object({
  id: z.number(),
  balance: z.number(),
});

type Account = z.infer<typeof AccountSchema>;   // the TS type, derived — never written by hand
```

That `z.infer` line is the core trick: **one declaration produces both the runtime check and the static type**, so they cannot drift apart. And "parse, don't validate" is the usage philosophy — you don't ask "is this valid?", you push data *through* the schema and get typed data out:

```typescript
const account = AccountSchema.parse(await res.json());   // throws loudly, at the boundary, if wrong
// or, when failure is expected and you want a typed result instead of an exception:
const result = AccountSchema.safeParse(raw);
if (!result.success) console.log(result.error.issues);   // precise, per-field failures
else result.data;                                        // fully typed from here on
```

Now the renamed-field bug fails *at the fetch*, with an error naming `balance`, instead of somewhere downstream with an error naming nothing. Wrap your API fetcher's return in `schema.parse` and every backend contract break becomes loud and located. This is the runtime half of contract safety; the build-time half — generating these schemas from the backend's OpenAPI spec so they can't drift either — is in [06/02](../06_testing_and_migrations/02_test_pyramid_mocking_contracts.md).

## 2. Building Schemas: Constraints, Transforms, Cross-Field Rules (How)

Schemas grow the same way Pydantic models do — types first, then constraints, then rules. Here's a registration schema that exercises the whole ladder:

```typescript
// Gist: registrationSchema.ts
import { z } from 'zod';

export const registrationSchema = z
  .object({
    username: z
      .string()
      .min(3, 'At least 3 characters')
      .regex(/^[a-zA-Z0-9_]+$/, 'Letters, numbers and underscores only')
      .transform((s) => s.toLowerCase()),        // normalize WHILE parsing
    email: z.string().email('Enter a valid email'),
    password: z
      .string()
      .min(8, 'At least 8 characters')
      .regex(/[A-Z]/, 'Needs an uppercase letter')
      .regex(/[0-9]/, 'Needs a number'),
    confirmPassword: z.string(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: 'Passwords do not match',
    path: ['confirmPassword'],   // attach the error to the field the user must fix
  });

export type RegistrationData = z.infer<typeof registrationSchema>;
```

Three things to notice. Every constraint carries its own **user-facing message** — the schema is simultaneously the rule and its explanation, one place to maintain both. The `.transform` on username means the parsed output is *already normalized*; like Pydantic's `mode="before"` validators, cleaning happens inside the boundary so the rest of the app never sees raw input. And `.refine` handles what per-field rules can't — comparing two fields — with `path` steering the error to the field where the user can act on it.

One more tool mirrors its Pydantic twin exactly: when an API returns several payload shapes distinguished by a tag field, `z.discriminatedUnion('kind', [DepositSchema, TransferSchema])` validates against the one matching branch and produces a TypeScript union the compiler can exhaustively check.

## 3. The Problem Formik Solves: Forms Are a State Machine You Keep Rebuilding

Now the second problem. Wire up a form with raw `useState` and count what you end up tracking: a value per field, whether each field has been **touched** (you don't want "Passwords do not match" screaming at someone who hasn't reached that field yet), the current validation errors, whether a submit is in flight, and whether to disable the button. Five kinds of state, re-implemented slightly differently in every form in the app.

Formik packages that state machine into one hook. It owns values, touched-ness, errors, and submission state; you supply what varies — initial values, how to validate, what submitting does:

```tsx
// Gist: RegistrationForm.tsx
import { useFormik } from 'formik';
import { registrationSchema, RegistrationData } from './registrationSchema';

export function RegistrationForm() {
  const formik = useFormik<RegistrationData>({
    initialValues: { username: '', email: '', password: '', confirmPassword: '' },

    // The bridge: run Formik's values through the Zod schema, and translate
    // Zod's issue list into Formik's { fieldName: message } error shape.
    validate: (values) => {
      const result = registrationSchema.safeParse(values);
      if (result.success) return {};
      const errors: Record<string, string> = {};
      for (const issue of result.error.issues) {
        const field = issue.path[0]?.toString();
        if (field && !errors[field]) errors[field] = issue.message;  // first issue per field
      }
      return errors;
    },

    onSubmit: async (values, { setSubmitting, resetForm }) => {
      try {
        await httpClient.post('/auth/register', values);
        resetForm();
      } finally {
        setSubmitting(false);
      }
    },
  });

  return (
    <form onSubmit={formik.handleSubmit}>
      <input
        name="username"
        value={formik.values.username}
        onChange={formik.handleChange}
        onBlur={formik.handleBlur}   // blur is what marks a field "touched"
      />
      {formik.touched.username && formik.errors.username && (
        <p role="alert">{formik.errors.username}</p>
      )}

      {/* email, password, confirmPassword: same three-line pattern */}

      <button type="submit" disabled={formik.isSubmitting || !formik.isValid}>
        {formik.isSubmitting ? 'Registering…' : 'Register'}
      </button>
    </form>
  );
}
```

The line that makes forms feel polished is the error display condition: `touched.username && errors.username`. Validation runs on every keystroke, but errors only *show* once the user has visited and left the field — that's `handleBlur`'s entire job. Skip the touched check and the form opens covered in red, scolding the user for a form they haven't filled in yet.

Notice also how clean the division of labor stayed: Zod knows nothing about React; Formik knows nothing about your rules. The `validate` bridge is the only place they meet, which means the schema is independently testable and reusable — the same `registrationSchema` can validate the API response *and* the form.

## 4. The Honest Caveat: Formik's Architecture Is Aging

Formik keeps every field **controlled**: each keystroke updates Formik's state and re-renders the form tree. For a login form, irrelevant. For a fifty-field back-office form, it's measurable jank. React Hook Form, the current default for new projects, inverted the design — fields are uncontrolled (the DOM holds the values, read via refs), so typing doesn't re-render, and its `zodResolver` makes the Zod bridge a one-liner instead of our hand-written `validate`.

The interview posture: know Formik because existing codebases (including this prep's reference app) use it; know *why* RHF wins on rendering; and point out that your validation layer is portable either way — the schema doesn't care which form library calls it. That framing turns "do you know library X?" into a demonstration that you separate concerns.

## 5. Interview Angles

**"The backend already validates. Why validate on the frontend too?"** Because the two validations serve different masters. Frontend validation is UX — instant feedback without a round-trip. Backend validation is security — the client can be bypassed entirely, so the server trusts nothing ([04_pydantic.md](04_pydantic.md) is that gate). The duplication concern is solved at the source: derive both from one contract, OpenAPI-generated types and Zod schemas, so the rules physically can't diverge.

**"Why parse an API response you've already typed?"** Because the TypeScript type is erased — at runtime it's a belief about the network, and networks break beliefs. `schema.parse` in the fetcher converts a silent downstream crash into an immediate, field-named error at the boundary. The one-liner that lands: *types check my code; Zod checks their data.*

**"Where do cross-field rules like password confirmation belong?"** In the schema, via `.refine` with a `path` pointing at the field the user must fix — not in the component. Rules in the schema are testable without rendering anything and shared by every consumer of the schema; rules in handlers are copy-pasted and drift.
