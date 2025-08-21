<script lang="ts">
	import { ModeWatcher } from "mode-watcher";


	let { children } = $props();
</script>

<ModeWatcher themeColors={{ dark: "dark", light: "white" }} />
<svelte:head>
	<title>Lenovo Finder</title>
	<meta name="description" content="Advanced data table with filtering, sorting, pagination, and column management" />
</svelte:head>

<svelte:boundary>
	<div class="px-5 py-3 flex flex-row h-screen">
		{@render children()}
	</div>

	{#snippet pending()}
		<p>loading...</p>
	{/snippet}
</svelte:boundary>
