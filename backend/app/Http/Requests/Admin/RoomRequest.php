<?php

namespace App\Http\Requests\Admin;

use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Validation\Rule;

class RoomRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    public function rules(): array
    {
        $roomId = $this->route('room')?->id;

        return [
            'nama_ruangan' => [
                'required',
                'string',
                'max:50',
                Rule::unique('rooms', 'nama_ruangan')->ignore($roomId),
            ],
            'kapasitas' => ['nullable', 'integer', 'min:1', 'max:1000'],
            'lokasi' => ['nullable', 'string', 'max:100'],
            'status' => ['required', Rule::in(['tersedia', 'tidak tersedia'])],
        ];
    }

    public function messages(): array
    {
        return [
            'nama_ruangan.required' => 'Nama ruangan wajib diisi',
            'nama_ruangan.unique' => 'Nama ruangan sudah dipakai',
            'kapasitas.integer' => 'Kapasitas harus berupa angka',
            'kapasitas.min' => 'Kapasitas minimal 1',
            'status.required' => 'Status wajib dipilih',
            'status.in' => 'Status tidak valid',
        ];
    }
}