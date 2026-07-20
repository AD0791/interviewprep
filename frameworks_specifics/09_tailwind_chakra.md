# Tailwind + Chakra, From Zero

Styling is the part of the stack where "it works" and "it will still work in a year" diverge fastest. This article explains the actual problem — CSS at scale — then builds up Tailwind's answer, shows where component libraries like Chakra earn their place, and ends with the pattern that uses each for what it's good at.

---

## 1. The Problem: CSS Only Grows

Traditional CSS starts clean: a stylesheet, some classes, `.transaction-card { ... }`. The rot sets in through three mechanisms, and every team rediscovers them.

First, **naming**. Every style needs a name, names need conventions (BEM, anyone?), and inventing `transaction-card__header--collapsed` for a one-off tweak is friction on every single change. Second, **the append-only stylesheet**. Six months in, nobody deletes CSS — you can't tell what still uses `.legacy-panel`, and the blast radius of removing it is unknowable, so the file only grows. Dead styles ship to users forever. Third, **specificity wars**: two rules fight over an element, someone adds `!important`, and now there are three rules fighting.

Notice what all three have in common: they come from styles living *far from* the components that use them, connected only by name strings. Tailwind's bet is to delete the distance.

## 2. Utility-First: Styles That Live Where They're Used

Tailwind gives you thousands of tiny single-purpose classes — `p-4` is padding, `flex` is display, `text-gray-400` is color — and you compose them directly in the markup:

```tsx
// A transaction card, no stylesheet, no names invented
function TransactionCard({ tx }: { tx: Transaction }) {
  return (
    <div className="rounded-xl border border-gray-800 bg-gray-900 p-6">
      <h3 className="text-xs font-bold uppercase text-gray-400">{tx.label}</h3>
      <p className="mt-2 text-2xl font-black">${tx.amount.toFixed(2)}</p>
    </div>
  );
}
```

Your first reaction is probably the correct one: *that markup is busy.* Hold that thought for section 4, because it's the real objection and it has a real answer. First, look at what each scale-problem turned into. Naming: gone — there is nothing to name. Deletion: automatic — delete the component and its styles go with it, because they were never anywhere else; and at build time Tailwind scans your source and emits **only the classes you actually used**, so the shipped CSS stays small and stops growing with the app's age. Specificity: gone — one class, one property, nothing competes.

There's a second-order benefit that only shows up in teams: the class list is a *bounded vocabulary*. `p-4` and `p-6` exist; `padding: 17px` does not. Two developers styling two cards independently land on the same spacing scale without coordinating.

## 3. The Theme Is the Design System (How)

That vocabulary is defined in one file, and this file — not the utility classes — is what senior styling conversations are about:

```javascript
// Gist: tailwind.config.js
module.exports = {
  content: ["./src/**/*.{ts,tsx}"],   // where the build-time scanner looks
  darkMode: 'class',                  // dark styles apply under <html class="dark">
  theme: {
    extend: {
      colors: {
        banking: {
          bg: '#030712',
          card: '#111827',
          accent: '#3b82f6',
        },
      },
    },
  },
};
```

Now `bg-banking-accent` is a class, and the brand color exists in exactly one place. These named values are **design tokens**, and the discipline that keeps a codebase consistent is simple to state: *components use tokens, never raw values.* A `bg-[#3b82f6]` arbitrary value in a PR is the smell — it's a magic number that the next rebrand won't find. Dark mode falls out of the same structure: with `darkMode: 'class'`, writing `bg-white dark:bg-banking-bg` makes theme switching a one-class toggle on `<html>`, because every component already declared both faces.

## 4. The Repetition Objection, Answered Properly

Back to the busy markup. Build three more cards and you'll be copy-pasting `rounded-xl border border-gray-800 bg-gray-900 p-6` — repetition, the thing good engineers are allergic to. Tailwind's escape hatch, `@apply` (bundling utilities into a CSS class), looks like the fix. Mostly resist it: name a bundle `.card` in a stylesheet and you've reinvented the distant, named, undeletable CSS you left behind.

The right unit of reuse in a React codebase is the one you already have — **the component**:

```tsx
// Gist: Card.tsx — the class string exists ONCE, behind a component API
export function Card({ children, className = '' }: CardProps) {
  return (
    <div className={`rounded-xl border border-gray-800 bg-gray-900 p-6 ${className}`}>
      {children}
    </div>
  );
}
```

Every card in the app is `<Card>`, restyling every card is a one-line change, and deleting `Card` deletes its styles. Utilities for one-off styling, components for repeated patterns — that division answers the verbosity objection completely, and it's the answer to give when an interviewer pokes at Tailwind's ugliness.

## 5. Where Chakra Earns Its Place: Behavior, Not Looks (Why)

Now try to build a modal dialog with Tailwind. The *appearance* takes five minutes: overlay, centered panel, shadow. Then the actual requirements arrive: focus must move into the dialog when it opens and be **trapped** there while it's open; Escape must close it; clicking the overlay must close it; focus must return to the button that opened it; and screen readers need `role="dialog"`, `aria-modal`, and a labelled title. None of that is styling — it's *interactive behavior with accessibility rules*, it's genuinely hard to get right, and Tailwind, being only CSS, offers nothing.

This is what component libraries are for. Chakra UI ships components with the behavior already correct:

```tsx
import { Modal, ModalOverlay, ModalContent, ModalHeader,
         ModalBody, ModalCloseButton, useDisclosure } from '@chakra-ui/react';

function LimitsEditor() {
  const { isOpen, onOpen, onClose } = useDisclosure();
  return (
    <>
      <button onClick={onOpen} className="rounded-lg bg-banking-accent px-4 py-2">
        Adjust limits
      </button>
      <Modal isOpen={isOpen} onClose={onClose} isCentered>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Adjust limits</ModalHeader>
          <ModalCloseButton />
          <ModalBody>{/* form here */}</ModalBody>
        </ModalContent>
      </Modal>
    </>
  );
}
```

Focus trapping, Escape, focus restoration, ARIA — all present, none written by you. That's the honest division of the two tools, and the pattern this repo's reference app uses: **Tailwind for layout and visual styling** (zero runtime cost — it's just compiled CSS), **Chakra for the interactive components where accessibility is hard** — modals, menus, tooltips, tabs. The cost worth naming: Chakra styles through CSS-in-JS at runtime, so its themed props carry a rendering cost Tailwind classes don't — one more reason to keep it scoped to the components that need its behavior. To keep the two visually coherent, mirror the same design tokens into Chakra's theme (`extendTheme` with the same `banking` colors), so both systems draw from one palette.

## 6. Interview Angles

**"Why has utility-first CSS won, when the markup is objectively uglier?"** Because it fixed the *scale* problems: nothing to name, dead styles impossible (deleted with their component, purged at build), no specificity conflicts, and shipped CSS that tracks design complexity instead of project age. The verbosity is real and answered by component extraction — the class string lives once, behind `<Card>`. Conceding the ugliness before defending the tradeoff is what makes the answer credible.

**"How do you keep styling consistent across a team?"** Tokens in the theme config as the only vocabulary, a review norm against arbitrary values like `bg-[#123456]`, repeated patterns promoted to shared components, and accessibility-heavy widgets delegated to a component library instead of hand-rolled. The theme file is effectively the design system's API — most consistency failures are someone routing around it.

**"Tailwind or a component library?"** Wrong question — they solve different layers. Tailwind is a styling system (how things look); Chakra is a behavior system (how modals, menus, and focus actually work, accessibly). The mature setup composes them: utilities for layout and skin, library components where WAI-ARIA behavior is hard, one shared token palette so the seam doesn't show.
