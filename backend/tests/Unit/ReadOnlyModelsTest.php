<?php

namespace Tests\Unit;

use App\Models\ClassificationResult;
use App\Models\OccupancyLog;
use LogicException;
use PHPUnit\Framework\TestCase;

class ReadOnlyModelsTest extends TestCase
{
    public function test_classification_result_cannot_be_saved(): void
    {
        $this->expectException(LogicException::class);
        $this->expectExceptionMessage('Tabel classification_results bersifat hanya-baca (read-only) untuk Laravel.');

        $model = new ClassificationResult();
        $model->save();
    }

    public function test_classification_result_cannot_be_updated(): void
    {
        $this->expectException(LogicException::class);
        $this->expectExceptionMessage('Tabel classification_results bersifat hanya-baca (read-only) untuk Laravel.');

        $model = new ClassificationResult();
        $model->update(['status' => 'sesuai_jadwal']);
    }

    public function test_classification_result_cannot_be_deleted(): void
    {
        $this->expectException(LogicException::class);
        $this->expectExceptionMessage('Tabel classification_results bersifat hanya-baca (read-only) untuk Laravel.');

        $model = new ClassificationResult();
        $model->delete();
    }

    public function test_occupancy_log_cannot_be_saved(): void
    {
        $this->expectException(LogicException::class);
        $this->expectExceptionMessage('Tabel occupancy_logs bersifat hanya-baca (read-only) untuk Laravel.');

        $model = new OccupancyLog();
        $model->save();
    }

    public function test_occupancy_log_cannot_be_updated(): void
    {
        $this->expectException(LogicException::class);
        $this->expectExceptionMessage('Tabel occupancy_logs bersifat hanya-baca (read-only) untuk Laravel.');

        $model = new OccupancyLog();
        $model->update(['is_occupied' => true]);
    }

    public function test_occupancy_log_cannot_be_deleted(): void
    {
        $this->expectException(LogicException::class);
        $this->expectExceptionMessage('Tabel occupancy_logs bersifat hanya-baca (read-only) untuk Laravel.');

        $model = new OccupancyLog();
        $model->delete();
    }
}
