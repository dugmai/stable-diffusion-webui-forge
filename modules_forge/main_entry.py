import gradio as gr

from modules import shared_items, shared, ui_common, sd_models
from modules import sd_vae as sd_vae_module
from modules_forge import main_thread


ui_checkpoint: gr.Dropdown = None
ui_vae: gr.Dropdown = None
ui_clip_skip: gr.Slider = None


def make_checkpoint_manager_ui():
    global ui_checkpoint, ui_vae, ui_clip_skip

    if shared.opts.sd_model_checkpoint in [None, 'None', 'none', '']:
        if len(sd_models.checkpoints_list) == 0:
            sd_models.list_models()
        if len(sd_models.checkpoints_list) > 0:
            shared.opts.set('sd_model_checkpoint', next(iter(sd_models.checkpoints_list.keys())))

    sd_model_checkpoint_args = lambda: {"choices": shared_items.list_checkpoint_tiles(shared.opts.sd_checkpoint_dropdown_use_short)}
    ui_checkpoint = gr.Dropdown(
        value=shared.opts.sd_model_checkpoint,
        label="Checkpoint",
        **sd_model_checkpoint_args()
    )
    ui_common.create_refresh_button(ui_checkpoint, shared_items.refresh_checkpoints, sd_model_checkpoint_args, f"forge_refresh_checkpoint")

    sd_vae_args = lambda: {"choices": shared_items.sd_vae_items()}
    ui_vae = gr.Dropdown(
        value="Automatic",
        label="VAE",
        **sd_vae_args()
    )
    ui_common.create_refresh_button(ui_vae, shared_items.refresh_vae_list, sd_vae_args, f"forge_refresh_vae")

    ui_clip_skip = gr.Slider(label="Clip skip", value=shared.opts.CLIP_stop_at_last_layers, **{"minimum": 1, "maximum": 12, "step": 1})

    return


def model_load_entry():
    sd_models.load_model()
    return


def checkpoint_change(ckpt_name):
    print(f'Checkpoint Selected: {ckpt_name}')
    shared.opts.set('sd_model_checkpoint', ckpt_name)
    shared.opts.save(shared.config_filename)

    model_load_entry()
    return


def vae_change(vae_name):
    print(f'VAE Selected: {vae_name}')
    shared.opts.set('sd_vae', vae_name)
    sd_vae_module.reload_vae_weights()
    return


def clip_skip_change(clip_skip):
    print(f'CLIP SKIP Selected: {clip_skip}')
    shared.opts.set('CLIP_stop_at_last_layers', clip_skip)
    return


def forge_main_entry():
    ui_checkpoint.change(lambda x: main_thread.async_run(checkpoint_change, x), inputs=[ui_checkpoint], show_progress=False)
    ui_vae.change(lambda x: main_thread.async_run(vae_change, x), inputs=[ui_vae], show_progress=False)
    ui_clip_skip.change(lambda x: main_thread.async_run(clip_skip_change, x), inputs=[ui_clip_skip], show_progress=False)

    # Load Model
    main_thread.async_run(model_load_entry)
    return