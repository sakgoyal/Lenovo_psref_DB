<script lang="ts">
	import { ModeWatcher } from "mode-watcher";
	let { children } = $props();
</script>

<ModeWatcher themeColors={{ dark: "dark", light: "white" }} />

<svelte:boundary>
	<div class="px-5 py-3">
		{@render children()}
	</div>

	{#snippet pending()}
		<p>loading...</p>
	{/snippet}
</svelte:boundary>
