<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { fetchAllMissionProgress } from '@/services/leaderboard'

const loading = ref(true)
const error = ref<string | null>(null)
const rows = ref<any[]>([])

onMounted(async () => {
    try {
        rows.value = await fetchAllMissionProgress()
    } catch (err) {
        error.value = 'Failed to load leaderboard analytics.'
    } finally {
        loading.value = false
    }
})

const leaderboard = computed(() => {
    const map = new Map()

    for (const entry of rows.value) {
        if (!map.has(entry.user_id)) {
            map.set(entry.user_id, {
                user_id: entry.user_id,
                total_score: 0,
                missions_completed: 0,
            })
        }

        const user = map.get(entry.user_id)
        user.total_score += entry.score
        user.missions_completed += 1
    }

    const list = Array.from(map.values())

    list.sort((a, b) => b.total_score - a.total_score)

    return list.map((u, index) => ({
        ...u,
        rank: index + 1,
        avg_score: u.missions_completed > 0 
            ? Math.round((u.total_score / u.missions_completed) * 100) / 100 
            : 0,
        tier: u.total_score >= 1000 ? 'Gold'
            : u.total_score >= 500 ? 'Silver'
            : 'Bronze'
    }))
})
</script>
