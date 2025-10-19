<script setup lang="ts">
import { ref, onMounted } from 'vue'
import {
  listProjects, createProject, deleteProject,
  listChatsInProject, listChats, createUnassignedChat,
  updateChat, deleteChat, listTrash, restoreChat,
  deleteChatPermanent,
  type Project, type Chat
} from '@/lib/chatApi'

import {
  SidebarGroup, SidebarGroupLabel, SidebarGroupContent,
  SidebarMenu, SidebarMenuItem, SidebarMenuButton
} from '@/components/ui/sidebar'
import { Button } from '@/components/ui/button'
import { Plus, Folder, MessageSquare, Trash2, MoreHorizontal, Undo2 } from 'lucide-vue-next'
import {
  DropdownMenu, DropdownMenuTrigger, DropdownMenuContent,
  DropdownMenuItem, DropdownMenuSeparator, DropdownMenuSub,
  DropdownMenuSubTrigger, DropdownMenuSubContent
} from '@/components/ui/dropdown-menu'

const loading = ref(false)
const projects = ref<Project[]>([])
const chatsByProject = ref<Record<number, Chat[]>>({})
const unassigned = ref<Chat[]>([])
const trash = ref<Chat[]>([])

async function loadAll() {
  loading.value = true
  try {
    projects.value = await listProjects()
    for (const p of projects.value) {
      chatsByProject.value[p.id] = await listChatsInProject(p.id)
    }
    unassigned.value = await listChats({ unassigned: true })
    trash.value = await listTrash()
  } finally {
    loading.value = false
  }
}
onMounted(loadAll)

/** Actions */
async function onNewProject() {
  const name = prompt('Project name')
  if (!name) return
  const p = await createProject(name)
  projects.value.unshift(p)
  chatsByProject.value[p.id] = []
}

async function onNewChatUnassigned() {
  const title = prompt('Chat title') || 'New chat'
  const c = await createUnassignedChat(title)
  unassigned.value.unshift(c)
  navigateTo(`/p/0/c/${c.id}`)
}

async function onNewChatInProject(pid: number) {
  const title = prompt('Chat title') || 'New chat'
  // можно было бы вызвать createChatInProject(pid, title),
  // но чтобы не плодить обёртки — создадим и сразу переместим
  const c = await createUnassignedChat(title)
  await moveChat(c, pid)
  navigateTo(`/p/${pid}/c/${c.id}`)
}

async function moveChat(c: Chat, pid: number | null) {
  const updated = await updateChat(c.id, { project_id: pid })
  // убрать из предыдущего списка
  if (c.project_id == null) {
    unassigned.value = unassigned.value.filter(x => x.id !== c.id)
  } else {
    chatsByProject.value[c.project_id] = (chatsByProject.value[c.project_id] || []).filter(x => x.id !== c.id)
  }
  // добавить в новый
  if (updated.project_id == null) {
    unassigned.value.unshift(updated)
  } else {
    chatsByProject.value[updated.project_id] = [updated, ...(chatsByProject.value[updated.project_id] || [])]
  }
}

async function renameChat(c: Chat) {
  const title = prompt('New title', c.title)
  if (!title || title.trim() === c.title) return
  const updated = await updateChat(c.id, { title: title.trim() })
  if (updated.project_id == null) {
    const i = unassigned.value.findIndex(x => x.id === c.id); if (i >= 0) unassigned.value[i] = updated
  } else {
    const arr = chatsByProject.value[updated.project_id] || []
    const i = arr.findIndex(x => x.id === c.id); if (i >= 0) arr[i] = updated
  }
}

async function removeChat(c: Chat) {
  if (!confirm(`Delete chat "${c.title}"?`)) return
  await deleteChat(c.id)
  if (c.project_id == null) {
    unassigned.value = unassigned.value.filter(x => x.id !== c.id)
  } else {
    chatsByProject.value[c.project_id] = (chatsByProject.value[c.project_id] || []).filter(x => x.id !== c.id)
  }
  trash.value = await listTrash()
}

async function restore(c: Chat) {
  const upd = await restoreChat(c.id)
  trash.value = trash.value.filter(x => x.id !== c.id)
  if (upd.project_id == null) {
    unassigned.value.unshift(upd)
  } else {
    chatsByProject.value[upd.project_id] = [upd, ...(chatsByProject.value[upd.project_id] || [])]
  }
}

async function deleteForever(c: Chat) {
  if (!confirm(`Permanently delete chat "${c.title}"? This cannot be undone.`)) return
  await deleteChatPermanent(c.id)
  trash.value = trash.value.filter(x => x.id !== c.id)
}

async function removeProject(p: Project) {
  if (!confirm(`Delete project "${p.name}" and all its chats?`)) return
  await deleteProject(p.id, 'hard') // 'trash' — если хочешь сначала в корзину
  projects.value = projects.value.filter(x => x.id !== p.id)
  delete chatsByProject.value[p.id]
  // обновим корзину на случай режима 'trash'
  trash.value = await listTrash()
}
</script>

<template>
  <SidebarGroup>
    <SidebarGroupLabel class="flex items-center justify-between">
      Chats
      <div class="flex items-center gap-1">
        <Button size="sm" variant="outline" @click="onNewChatUnassigned">+ New Chat</Button>
        <Button size="icon" variant="ghost" title="New project" @click="onNewProject">
          <Plus class="h-4 w-4" />
        </Button>
      </div>
    </SidebarGroupLabel>

    <SidebarGroupContent>

      <!-- Unassigned -->
      <div class="px-2 mt-2 text-xs uppercase tracking-wide text-muted-foreground">Unassigned</div>
      <SidebarMenu class="ml-1">
        <SidebarMenuItem
          v-for="c in unassigned"
          :key="c.id"
          class="flex items-center gap-1"
        >
          <SidebarMenuButton asChild class="flex-1">
            <NuxtLink :to="`/p/0/c/${c.id}`" class="flex items-center gap-2">
              <MessageSquare class="h-4 w-4" />
              <span class="truncate">{{ c.title }}</span>
            </NuxtLink>
          </SidebarMenuButton>

          <!-- ⋯ справа -->
          <DropdownMenu>
            <DropdownMenuTrigger as-child>
              <Button variant="ghost" size="icon" class="h-7 w-7">
                <MoreHorizontal class="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" class="w-48">
              <DropdownMenuItem @click="renameChat(c)">Rename</DropdownMenuItem>
              <DropdownMenuSub>
                <DropdownMenuSubTrigger>Move to Project</DropdownMenuSubTrigger>
                <DropdownMenuSubContent>
                  <DropdownMenuItem @click="moveChat(c, null)">Unassigned</DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem
                    v-for="p in projects"
                    :key="p.id"
                    @click="moveChat(c, p.id)"
                  >
                    <Folder class="h-3 w-3 mr-2" /> {{ p.name }}
                  </DropdownMenuItem>
                </DropdownMenuSubContent>
              </DropdownMenuSub>
              <DropdownMenuSeparator />
              <DropdownMenuItem class="text-red-600" @click="removeChat(c)">Delete</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </SidebarMenuItem>
      </SidebarMenu>

      <!-- Projects -->
      <div class="px-2 mt-3 text-xs uppercase tracking-wide text-muted-foreground">Projects</div>

      <template v-for="p in projects" :key="p.id">
        <!-- Заголовок проекта с кнопками справа -->
        <div class="px-2 mt-2 text-xs flex items-center gap-2 text-muted-foreground">
          <Folder class="h-3 w-3" /> <span class="truncate">{{ p.name }}</span>

          <div class="ml-auto flex items-center gap-1">
            <Button size="icon" variant="ghost" title="New chat"
                    @click="onNewChatInProject(p.id)">
              <Plus class="h-3 w-3" />
            </Button>

            <DropdownMenu>
              <DropdownMenuTrigger as-child>
                <Button size="icon" variant="ghost" title="Project menu">
                  <MoreHorizontal class="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" class="w-44">
                <DropdownMenuItem class="text-red-600" @click="removeProject(p)">
                  Delete Project
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>

        <!-- Чаты проекта -->
        <SidebarMenu class="ml-1">
          <SidebarMenuItem
            v-for="c in (chatsByProject[p.id] || [])"
            :key="c.id"
            class="flex items-center gap-1"
          >
            <SidebarMenuButton asChild class="flex-1">
              <NuxtLink :to="`/p/${p.id}/c/${c.id}`" class="flex items-center gap-2">
                <MessageSquare class="h-4 w-4" />
                <span class="truncate">{{ c.title }}</span>
              </NuxtLink>
            </SidebarMenuButton>

            <!-- ⋯ справа -->
            <DropdownMenu>
              <DropdownMenuTrigger as-child>
                <Button variant="ghost" size="icon" class="h-7 w-7">
                  <MoreHorizontal class="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" class="w-48">
                <DropdownMenuItem @click="renameChat(c)">Rename</DropdownMenuItem>
                <DropdownMenuSub>
                  <DropdownMenuSubTrigger>Move to Project</DropdownMenuSubTrigger>
                  <DropdownMenuSubContent>
                    <DropdownMenuItem @click="moveChat(c, null)">Unassigned</DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem
                      v-for="pp in projects"
                      :key="pp.id"
                      @click="moveChat(c, pp.id)"
                    >
                      <Folder class="h-3 w-3 mr-2" /> {{ pp.name }}
                    </DropdownMenuItem>
                  </DropdownMenuSubContent>
                </DropdownMenuSub>
                <DropdownMenuSeparator />
                <DropdownMenuItem class="text-red-600" @click="removeChat(c)">Delete</DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </SidebarMenuItem>
        </SidebarMenu>
      </template>

      <!-- Trash -->
      <div class="px-2 mt-4 text-xs uppercase tracking-wide text-muted-foreground flex items-center gap-2">
        <Trash2 class="h-3 w-3" /> Trash
      </div>
      <SidebarMenu class="ml-1">
        <SidebarMenuItem v-for="c in trash" :key="c.id" class="flex items-center justify-between gap-2">
          <div class="flex items-center gap-2 flex-1 opacity-70 line-through">
            <MessageSquare class="h-4 w-4" />
            <span class="truncate">{{ c.title }}</span>
          </div>
          <div class="flex gap-1">
            <Button size="sm" variant="ghost" class="h-6" title="Restore" @click="restore(c)">
              <Undo2 class="h-4 w-4" />
            </Button>
            <Button size="sm" variant="ghost" class="h-6 text-red-600" title="Delete permanently" @click="deleteForever(c)">
              <Trash2 class="h-4 w-4" />
            </Button>
          </div>
        </SidebarMenuItem>
      </SidebarMenu>

      <div v-if="loading" class="px-2 py-1 text-xs text-muted-foreground">Loading…</div>
    </SidebarGroupContent>
  </SidebarGroup>
</template>