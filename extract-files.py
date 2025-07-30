#!/usr/bin/env -S PYTHONPATH=../../../tools/extract-utils python3
#
# SPDX-FileCopyrightText: 2024 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0
#

from extract_utils.fixups_blob import (
    BlobFixupCtx,
    File,
    blob_fixup,
    blob_fixups_user_type,
)
from extract_utils.fixups_lib import (
    lib_fixups,
)
from extract_utils.main import (
    ExtractUtils,
    ExtractUtilsModule,
)
from extract_utils.tools import (
    llvm_objdump_path,
)
from extract_utils.utils import (
    run_cmd,
)

namespace_imports = [
    'hardware/oplus',
    'vendor/oneplus/sm8450-common',
    'hardware/qcom-caf/sm8450',
    'vendor/qcom/opensource/commonsys-intf/display',
    'vendor/qcom/opensource/commonsys/display',
]


def blob_fixup_nop_call(
    ctx: BlobFixupCtx,
    file: File,
    file_path: str,
    call_instruction: str,
    disassemble_symbol: str,
    symbol: str,
    *args,
    **kwargs,
):
    for line in run_cmd(
        [
            llvm_objdump_path,
            f'--disassemble-symbols={disassemble_symbol}',
            file_path,
        ]
    ).splitlines():
        line = line.split(maxsplit=3)

        if len(line) != 4:
            continue

        offset, _, instruction, args = line

        if instruction != call_instruction:
            continue

        if not args.endswith(f' <{symbol}>'):
            continue

        with open(file_path, 'rb+') as f:
            f.seek(int(offset[:-1], 16))
            f.write(b'\x1f\x20\x03\xd5')  # AArch64 NOP

        break


blob_fixups: blob_fixups_user_type = {
    'odm/bin/hw/vendor.oplus.hardware.biometrics.fingerprint@2.1-service': blob_fixup()
        .replace_needed('android.hardware.biometrics.common-V1-ndk_platform.so', 'android.hardware.biometrics.common-V1-ndk.so')
        .replace_needed('android.hardware.biometrics.fingerprint-V1-ndk_platform.so', 'android.hardware.biometrics.fingerprint-V1-ndk.so'),
    'odm/etc/camera/CameraHWConfiguration.config': blob_fixup()
        .regex_replace('SystemCamera =  0;  0;  1;  1;  1', 'SystemCamera =  0;  0;  0;  0;  1'),
    ('odm/lib64/libCOppLceTonemapAPI.so', 'odm/lib64/libPerfectColor.so', 'odm/lib64/libSuperRaw.so', 'odm/lib64/libYTCommon.so', 'odm/lib64/libaps_frame_registration.so', 'odm/lib64/libyuv2.so'): blob_fixup()
        .replace_needed('libstdc++.so', 'libstdc++_vendor.so'),
    ('odm/lib64/libAlgoProcess.so', 'vendor/lib64/libcamximageformatutils.so'): blob_fixup()
        .replace_needed('android.hardware.graphics.common-V2-ndk_platform.so', 'android.hardware.graphics.common-V6-ndk.so')
        .replace_needed('vendor.qti.hardware.display.config-V2-ndk_platform.so', 'vendor.qti.hardware.display.config-V5-ndk.so'),
    ('odm/lib64/libHIS.so', 'odm/lib64/libOGLManager.so'): blob_fixup()
        .clear_symbol_version('AHardwareBuffer_allocate')
        .clear_symbol_version('AHardwareBuffer_describe')
        .clear_symbol_version('AHardwareBuffer_lock')
        .clear_symbol_version('AHardwareBuffer_release')
        .clear_symbol_version('AHardwareBuffer_unlock'),
    ('odm/lib64/libaiboost_hexagon.so', 'odm/lib64/libarcsoft_high_dynamic_range_v4.so'): blob_fixup()
        .clear_symbol_version('remote_handle_close')
        .clear_symbol_version('remote_handle_invoke')
        .clear_symbol_version('remote_handle_open')
        .clear_symbol_version('remote_handle64_close')
        .clear_symbol_version('remote_handle64_invoke')
        .clear_symbol_version('remote_handle64_open')
        .clear_symbol_version('remote_register_buf_attr')
        .clear_symbol_version('remote_register_buf'),
    ('odm/lib64/libarcsoft_dual_sat.so', 'odm/lib64/libarcsoft_dual_zoomtranslator.so', 'odm/lib64/libarcsoft_triple_sat.so', 'odm/lib64/libarcsoft_triple_zoomtranslator.so'): blob_fixup()
        .add_needed('libc++_shared.so'),
    'odm/lib64/libextensionlayer.so': blob_fixup()
        .replace_needed('libziparchive.so', 'libziparchive_odm.so'),
    'vendor/etc/libnfc-nci.conf': blob_fixup()
        .regex_replace('NFC_DEBUG_ENABLED=1', 'NFC_DEBUG_ENABLED=0'),
    'vendor/etc/libnfc-nxp.conf': blob_fixup()
        .regex_replace('(NXPLOG_.*_LOGLEVEL)=0x03', '\\1=0x02')
        .regex_replace('NFC_DEBUG_ENABLED=1', 'NFC_DEBUG_ENABLED=0'),
    'vendor/lib64/libmidasserviceintf_aidl.so': blob_fixup()
        .replace_needed('android.frameworks.stats-V1-ndk_platform.so', 'android.frameworks.stats-V1-ndk.so'),
}  # fmt: skip

module = ExtractUtilsModule(
    'wly',
    'oneplus',
    namespace_imports=namespace_imports,
    blob_fixups=blob_fixups,
    lib_fixups=lib_fixups,
)

if __name__ == '__main__':
    utils = ExtractUtils.device_with_common(
        module, 'sm8450-common', module.vendor
    )
    utils.run()
