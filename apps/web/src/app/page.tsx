/**
 * Velour — Landing Page
 *
 * Displays the Velour brand name and tagline.
 * This is the initial landing page for the engineering foundation.
 */

export default function Home() {
  return (
    <main className="flex flex-1 flex-col items-center justify-center px-6">
      <div className="flex flex-col items-center gap-6 text-center">
        {/* Brand */}
        <h1 className="text-6xl font-bold tracking-tight sm:text-8xl bg-gradient-to-r from-accent-light to-accent bg-clip-text text-transparent">
          Velour
        </h1>

        {/* Tagline */}
        <p className="text-xl font-medium text-muted sm:text-2xl">
          AI Personal Stylist
        </p>

        {/* Subtle divider */}
        <div className="mt-4 h-px w-24 bg-gradient-to-r from-transparent via-accent/50 to-transparent" />

        {/* Status */}
        <div className="mt-2 flex items-center gap-2 rounded-full border border-border px-4 py-2 text-sm text-muted">
          <span className="relative flex h-2 w-2">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
            <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-500" />
          </span>
          Engineering Foundation Active
        </div>
      </div>
    </main>
  );
}
