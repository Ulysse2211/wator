<script setup lang="ts">
import { onKeyStroke } from '@vueuse/core'

const { public: { apiBase } } = useRuntimeConfig()
const platow = ref()
platow.value = await $fetch('/next_round', { baseURL: apiBase })

const historique = ref([platow.value])

const poissons = computed(() => platow.value.grid.flat().filter(Boolean))
const thons = computed(() => poissons.value.filter(p => p.type === 'T'))
const requins = computed(() => poissons.value.filter(p => p.type === 'R'))
const moy = (l: number[]) => l.length ? (l.reduce((a, b) => a + b, 0) / l.length).toFixed(2) : 0

async function update() {
  if (!thons.value.length || !requins.value.length) return
  platow.value = await $fetch('/next_round', { baseURL: apiBase })
  historique.value.push(platow.value)
}
async function reset() {
  platow.value = await $fetch('/reset', { baseURL: apiBase })
  historique.value = [platow.value]
}

onKeyStroke('Enter', (e) => {
  e.preventDefault()
  update()
})

onNuxtReady(() => {
  setInterval(() => {update()}, 3000)
})
</script>

<template>
  <div>
  <div class="absolute z-10 backdrop-blur-3xl flex flex-col items-center justify-center w-full h-full"
       v-if="(!thons.length || !requins.length)">
    Gagnant: {{ requins.length !== 0 ? 'Requins' : 'Thons' }}
    <button class="font-extrabold text-xl rounded-xl p-2 bg-red-900 hover:bg-red-950 text-white" @click="reset()">Reset</button>
  </div>
  <div class="bg-gray-100 gap-10 p-5 flex h-full w-full">
    <div>
      <div class="flex gap-5 items-center">
        <h1 class="font-bold text-5xl mb-5">Tour {{ platow.round }}</h1>
        <button class="font-extrabold text-xl rounded-xl p-2 bg-gray-600 hover:bg-gray-700 text-white" @click="update()">Tour suivant (Entrer)</button>
        <button class="font-extrabold text-xl rounded-xl p-2 bg-red-900 hover:bg-red-950 text-white" @click="reset()">Reset</button>
      </div>
      <div class="rounded-xl w-fit bg-linear-to-b from-sky-300 to-cyan-700 flex flex-row p-2">
      <div
          v-for="value in platow.grid"
          class="flex flex-col justify-center items-center">
        <div
            v-for="value2 in value"
            class="m-2 w-10 h-10 flex items-center justify-center border-2 border-b-black rounded-xl">
          <span v-if="value2 && value2.type === 'T'">🐟</span>
          <span v-else-if="value2 && value2.type === 'R'">🦈</span>
          <span v-else></span>
        </div>
      </div>
    </div>
    </div>
    <div>
      <h1 class="font-bold text-5xl mb-5">Stats</h1>
      <div class="flex flex-col items-start text-xl underline font-bold">
        <span>* Nombre de requins {{ requins.length }}</span>
        <span>* Nombre de thons {{ thons.length }}</span>
        <span>* Nombre total de poissons {{ poissons.length }}</span>
        <span>* Cases libres {{ platow.scale ** 2 - poissons.length }}</span>
        <span>* %age de requins {{ poissons.length ? (requins.length / poissons.length * 100).toFixed(1) : 0 }} %</span>
        <span>* %age de thons {{ poissons.length ? (thons.length / poissons.length * 100).toFixed(1) : 0 }} %</span>
        <span>* Power requins {{ requins.reduce((a, r) => a + r.energie, 0) }}</span>
        <span>* Power moyenne requins {{ moy(requins.map(r => r.energie)) }}</span>
        <span>* Requins qui vont bientot mourrir {{ requins.filter(r => r.energie <= 1).length }}</span>
        <span>* Thons qui vont passer une bonne soirée {{ thons.filter(t => t.age_gestation >= t.temps_gestation).length }}</span>
        <span>* Requins qui vont passer une bonne soirée {{ requins.filter(r => r.age_gestation >= r.temps_gestation).length }}</span>
        <span>* Max thons {{ Math.max(0, ...Object.values(platow.stats).map(s => s.thons)) }}</span>
        <span>* Max requins {{ Math.max(0, ...Object.values(platow.stats).map(s => s.shark)) }}</span>
      </div>
    </div>
  </div>
  </div>
</template>
