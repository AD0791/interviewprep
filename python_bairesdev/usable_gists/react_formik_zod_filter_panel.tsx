// Use Case: Schema-Validated React Filter Panel Form (Formik + Zod)
// Purpose: Validates date ranges and query parameters before API triggers.
// Key features: Zod schema, Formik validate adaptation, TypeScript type inferences.

import React from 'react';
import { useFormik } from 'formik';
import { z } from 'zod';

// 1. Define schema validation rules using Zod
export const filterSchema = z.object({
  startDate: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, 'Must be YYYY-MM-DD format'),
  endDate: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, 'Must be YYYY-MM-DD format'),
  tenantId: z.string().optional(),
  minAmount: z.coerce.number().min(0, 'Minimum amount cannot be negative').default(0),
}).refine((data) => new Date(data.startDate) <= new Date(data.endDate), {
  message: 'Start date cannot be after end date',
  path: ['startDate'], // Bind error to the startDate field
});

type FilterFormData = z.infer<typeof filterSchema>;

interface FilterPanelProps {
  onApplyFilters: (filters: FilterFormData) => void;
}

export const FilterPanel: React.FC<FilterPanelProps> = ({ onApplyFilters }) => {
  const formik = useFormik<FilterFormData>({
    initialValues: {
      startDate: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]!,
      endDate: new Date().toISOString().split('T')[0]!,
      tenantId: '',
      minAmount: 0,
    },
    // Custom validation bridge running values against Zod schema safely
    validate: (values) => {
      const result = filterSchema.safeParse(values);
      if (result.success) return {};

      const errors: Record<string, string> = {};
      for (const issue of result.error.issues) {
        const path = issue.path[0];
        if (path) {
          errors[path.toString()] = issue.message;
        }
      }
      return errors;
    },
    onSubmit: (values) => {
      onApplyFilters(values);
    },
  });

  return (
    <form onSubmit={formik.handleSubmit} className="p-4 bg-gray-900 text-white rounded-lg shadow-md flex gap-4 items-end">
      <div>
        <label className="block text-xs font-semibold uppercase text-gray-400">Start Date</label>
        <input
          name="startDate"
          type="date"
          onChange={formik.handleChange}
          onBlur={formik.handleBlur}
          value={formik.values.startDate}
          className="bg-gray-800 p-2 rounded text-white border border-gray-700 focus:outline-none"
        />
        {formik.touched.startDate && formik.errors.startDate && (
          <div className="text-red-500 text-xs mt-1">{formik.errors.startDate}</div>
        )}
      </div>
      <div>
        <label className="block text-xs font-semibold uppercase text-gray-400">End Date</label>
        <input
          name="endDate"
          type="date"
          onChange={formik.handleChange}
          onBlur={formik.handleBlur}
          value={formik.values.endDate}
          className="bg-gray-800 p-2 rounded text-white border border-gray-700 focus:outline-none"
        />
        {formik.touched.endDate && formik.errors.endDate && (
          <div className="text-red-500 text-xs mt-1">{formik.errors.endDate}</div>
        )}
      </div>
      <button type="submit" className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded font-bold text-white transition-colors">
        Apply Filters
      </button>
    </form>
  );
};
