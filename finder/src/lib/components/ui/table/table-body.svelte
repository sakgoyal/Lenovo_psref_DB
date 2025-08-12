<script lang="ts">
	import { cn, type WithElementRef } from "$lib/utils.js";
	import type { HTMLAttributes } from "svelte/elements";

	let {
		ref = $bindable(null),
		class: className,
		children,
		...restProps
	}: WithElementRef<HTMLAttributes<HTMLTableSectionElement>> = $props();
</script>

<tbody
	bind:this={ref}
	data-slot="table-body"
	class={cn("[&_tr:last-child]:border-0 [&_tr:nth-child(odd)]:bg-accent/30 text-foreground", className)}
	{...restProps}
>
	{@render children?.()}
</tbody>
