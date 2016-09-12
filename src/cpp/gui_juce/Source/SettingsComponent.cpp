//
//  SettingsComponent.cpp
//  gui_juce
//
//  Created by Juan Luis Salas García on 12/9/16.
//
//

#include <stdio.h>
#include "SettingsComponent.h"


/** @brief SettingsComponent constructor
 *
 * @param[in] parent_component Parent component of this one
 */
SettingsComponent::SettingsComponent(MainContentComponent* parent_component) {
    this->parent_component = parent_component;
    setOpaque (true);
    addAndMakeVisible (_folderButton);
    _folderButton.setButtonText("Choose experiment folder");
    _folderButton.addListener(this);
}

/** @brief Override callback to paint component
 */
void SettingsComponent::paint (Graphics& g)
{
    g.fillAll(Colour::fromFloatRGBA(0.7f, 0.777f, 0.517f, 1.0f));
}

/** @brief Override callback for resizing
 */
void SettingsComponent::resized()
{
    int percentage_x = getWidth() / 100;
    int percentage_y = getHeight() / 100;
    _folderButton.setBounds(1 * percentage_x, 2 * percentage_y,       // x, y
                            20 * percentage_x, 5 * percentage_y);     // width, height
}

/** @brief Callback when a button is clicked
 */
void SettingsComponent::buttonClicked(Button* b)
{
    /* Folder button
     * =============
     *
     * 1. Open directory dialog
     * 2. Set experiment folder
     *    - If exists: choose if load it or delete existing experiment
     */
    if (b == &_folderButton) {
        FileChooser fc ("Choose an experiment directory",
                        File::getCurrentWorkingDirectory(),
                        "*.",
                        true);
        if (fc.browseForDirectory())
        {
            ExperimentInterface* ei;
            if (parent_component->experiment_interface != nullptr)
                delete parent_component->experiment_interface;
            File chosenDirectory = fc.getResult();
            string full_directory_path = chosenDirectory.getFullPathName().toStdString();
            if (experimentAlreadyExists(full_directory_path)) {
                bool chosen_ok;
                chosen_ok = AlertWindow::showOkCancelBox (AlertWindow::QuestionIcon,
                                                          "Experiment already exists",
                                                          "Press OK to load existing experiment, or Cancel to delete it and start a new experiment.",
                                                          String(),
                                                          String(),
                                                          0);
                if (chosen_ok) {
                    ei = new ExperimentInterface(full_directory_path, false);
                } else {
                    ei =
                    new ExperimentInterface(full_directory_path, true);
                }
            } else {
                ei =
                new ExperimentInterface(full_directory_path, true);
            }
            parent_component->loadEcosystemInterface(ei);
        }
    }
}