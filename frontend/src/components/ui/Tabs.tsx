import { ReactNode } from 'react'

export type TabOption<T extends string> = {
  key: T
  label: string
}

export function Tabs<T extends string>(props: {
  value: T
  onChange: (v: T) => void
  tabs: TabOption<T>[]
  right?: ReactNode
}) {
  return (
    <div className="flex items-center justify-between gap-3">
      <div className="inline-flex items-center bg-slate-900 border border-slate-800 rounded-xl p-1">
        {props.tabs.map((t) => {
          const active = t.key === props.value
          return (
            <button
              key={t.key}
              onClick={() => props.onChange(t.key)}
              className={[
                'px-4 py-2 rounded-lg text-sm font-medium transition',
                active ? 'bg-slate-800 text-white' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60',
              ].join(' ')}
            >
              {t.label}
            </button>
          )
        })}
      </div>
      {props.right ? <div className="shrink-0">{props.right}</div> : null}
    </div>
  )
}



