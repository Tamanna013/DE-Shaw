import { GitCommit, FileText, Terminal } from 'lucide-react'

interface Evidence {
  type: string
  value: string
}

export function EvidenceList({ evidence }: { evidence: Evidence[] }) {
  if (!evidence || evidence.length === 0) {
    return <p className="text-sm italic text-muted-foreground">No direct evidence cited.</p>
  }

  const getIcon = (type: string) => {
    switch(type) {
      case 'commit': return <GitCommit className="w-4 h-4 text-orange-500" />
      case 'log': return <Terminal className="w-4 h-4 text-green-500" />
      default: return <FileText className="w-4 h-4 text-blue-500" />
    }
  }

  return (
    <ul className="grid gap-2 md:grid-cols-2">
      {evidence.map((item, i) => (
        <li key={i} className="flex items-center space-x-3 text-sm p-2 rounded border bg-background">
          <span className="flex-shrink-0 p-1.5 bg-muted rounded-md">
            {getIcon(item.type)}
          </span>
          <span className="font-mono text-xs truncate" title={item.value}>
            {item.value}
          </span>
        </li>
      ))}
    </ul>
  )
}
