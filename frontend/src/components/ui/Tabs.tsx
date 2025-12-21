import type { ReactNode } from 'react'

export type TabOption<T extends string> = {
  key: T
  label: string
  icon?: string
}

export function Tabs<T extends string>(props: {
  value: T
  onChange: (v: T) => void
  tabs: TabOption<T>[]
  right?: ReactNode
}) {
  return (
    <div className="flex items-center justify-between gap-3 overflow-x-auto pb-2">
      <div className="inline-flex items-center bg-slate-900 border border-slate-800 rounded-xl p-1 min-w-max">
        {props.tabs.map((t) => {
          const active = t.key === props.value
          return (
            <button
              key={t.key}
              onClick={() => props.onChange(t.key)}
              className={[
                'px-3 sm:px-4 py-2 rounded-lg text-sm font-medium transition whitespace-nowrap flex items-center gap-1.5',
                active ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60',
              ].join(' ')}
            >
              {t.icon && <span className="text-base">{t.icon}</span>}
              <span className="hidden sm:inline">{t.label}</span>
            </button>
          )
        })}
      </div>
      {props.right ? <div className="shrink-0">{props.right}</div> : null}
    </div>
  )
}





