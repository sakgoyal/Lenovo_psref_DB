import { prerender } from '$app/server';
import { db } from '$lib/schema';


export const getFilterValues = prerender(async () => {
	const filterValues = await db.$client.execute("SELECT * FROM filter_values WHERE column_name NOT IN ('Docking', 'Included Upgrade', 'Announce Date', 'Display', 'Standard Ports', 'Operating System', 'Dimensions (WxDxH)', 'Product', 'Processor', 'End of Support');");
	return filterValues.rows.map(row => ({
		column_name: row.column_name as string,
		value: JSON.parse(row.distinct_values_json ?? '[]') as string[],
	}));
});
