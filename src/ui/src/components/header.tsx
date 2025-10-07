export function Header() {
  return (
    <header className="sticky top-0 z-40 w-full border-b bg-white/80 backdrop-blur supports-[backdrop-filter]:bg-white/60">
      <div className="mx-auto w-full px-4 sm:px-6 lg:px-12 py-4 flex flex-col gap-1">
        <div className="flex items-baseline justify-between">
          <h1 className="text-2xl font-semibold tracking-tight text-gray-800">
            Open<span className="text-blue-600">Anonymiser</span>
          </h1>
        </div>
        <p className="text-sm text-gray-600">Document Anonymization Tool</p>
      </div>
    </header>
  );
}
