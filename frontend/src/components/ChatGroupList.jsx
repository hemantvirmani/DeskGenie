import { useState } from 'react'
import { Plus, MessageSquare, Trash2, Pencil, Check, X } from 'lucide-react'
import { UIStrings } from '../uiStrings'

function ChatGroupList({
  groups,
  activeGroupId,
  onSelectGroup,
  onNewGroup,
  onRenameGroup,
  onDeleteGroup
}) {
  const [editingId, setEditingId] = useState(null)
  const [editName, setEditName] = useState('')

  const startEditing = (group) => {
    setEditingId(group.id)
    setEditName(group.name)
  }

  const saveEdit = () => {
    if (editingId) {
      onRenameGroup(editingId, editName)
      setEditingId(null)
      setEditName('')
    }
  }

  const cancelEdit = () => {
    setEditingId(null)
    setEditName('')
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') saveEdit()
    if (e.key === 'Escape') cancelEdit()
  }

  return (
    <div className="flex flex-col flex-1 min-h-0">
      {/* New Chat Button */}
      <div className="p-3">
        <button
          onClick={onNewGroup}
          className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-white font-medium transition-colors"
        >
          <Plus className="w-4 h-4" />
          {UIStrings.NEW_CHAT_BUTTON}
        </button>
      </div>

      {/* Groups List */}
      <div className="flex-1 overflow-y-auto px-2">
        {groups.map(group => (
          <div
            key={group.id}
            className={`group flex items-center gap-2 px-3 py-2 rounded-lg mb-1 cursor-pointer transition-colors ${
              group.id === activeGroupId
                ? 'bg-slate-600'
                : 'hover:bg-slate-700'
            }`}
            onClick={() => editingId !== group.id && onSelectGroup(group.id)}
          >
            <MessageSquare className="w-4 h-4 text-slate-400 flex-shrink-0" />

            {editingId === group.id ? (
              // Editing mode
              <div className="flex-1 flex items-center gap-1">
                <input
                  type="text"
                  value={editName}
                  onChange={(e) => setEditName(e.target.value)}
                  onKeyDown={handleKeyDown}
                  className="flex-1 px-2 py-1 bg-slate-800 border border-slate-500 rounded text-sm text-white focus:outline-none focus:ring-1 focus:ring-blue-500"
                  autoFocus
                  onClick={(e) => e.stopPropagation()}
                />
                <button
                  onClick={(e) => { e.stopPropagation(); saveEdit() }}
                  className="p-1 hover:bg-slate-600 rounded"
                >
                  <Check className="w-3 h-3 text-green-400" />
                </button>
                <button
                  onClick={(e) => { e.stopPropagation(); cancelEdit() }}
                  className="p-1 hover:bg-slate-600 rounded"
                >
                  <X className="w-3 h-3 text-red-400" />
                </button>
              </div>
            ) : (
              // Display mode
              <>
                <span className="flex-1 text-sm text-slate-200 truncate">
                  {group.name}
                </span>
                <div className="hidden group-hover:flex items-center gap-1">
                  <button
                    onClick={(e) => { e.stopPropagation(); startEditing(group) }}
                    className="p-1 hover:bg-slate-600 rounded"
                    title={UIStrings.RENAME_CHAT}
                  >
                    <Pencil className="w-3 h-3 text-slate-400" />
                  </button>
                  <button
                    onClick={(e) => { e.stopPropagation(); onDeleteGroup(group.id) }}
                    className="p-1 hover:bg-slate-600 rounded"
                    title={UIStrings.DELETE_CHAT}
                  >
                    <Trash2 className="w-3 h-3 text-red-400" />
                  </button>
                </div>
              </>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

export default ChatGroupList
